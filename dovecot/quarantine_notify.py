#!/usr/bin/python3

import json
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import html2text
import MySQLdb
from jinja2 import Template

import redis

pid = str(os.getpid())
pidfile = "/tmp/quarantine_notify.pid"  # noqa: S108

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % (pidfile))
    sys.exit()

pid = str(os.getpid())
with open(pidfile, "w") as f:
    f.write(pid)

try:

    while True:
        try:
            r = redis.StrictRedis(
                host="redis",
                decode_responses=True,
                port=6379,
                db=0,
                password=os.environ["REDISPASS"],
            )
            r.ping()
        except Exception as ex:
            print("%s - trying again..." % (ex))
            time.sleep(3)
        else:
            break

    time_now = int(time.time())
    mail_hostname = os.environ.get("MAIL_HOSTNAME")

    max_score = float(r.get("Q_MAX_SCORE") or "9999.0")
    if max_score == "":
        max_score = 9999.0

    def query_mysql(query, headers=True, update=False):
        while True:
            try:
                cnx = MySQLdb.connect(
                    user=os.environ.get("DBUSER"),
                    password=os.environ.get("DBPASS"),
                    database=os.environ.get("DBNAME"),
                    charset="utf8mb4",
                    collation="utf8mb4_general_ci",
                )
            except Exception as ex:
                print("%s - trying again..." % (ex))
                time.sleep(3)
            else:
                break
        cur = cnx.cursor()
        cur.execute(query)
        if not update:
            result = []
            columns = tuple([d[0] for d in cur.description])
            for row in cur:
                if headers:
                    result.append(dict(list(zip(columns, row))))
                else:
                    result.append(row)
            cur.close()
            cnx.close()
            return result
        else:
            cnx.commit()
            cur.close()
            cnx.close()

    def notify_rcpt(rcpt, msg_count, quarantine_acl, category):
        if category == "add_header":
            category = "add header"
        meta_query = query_mysql(
            "SELECT SHA2(CONCAT(id, qid), 256) AS qhash, id, subject, score, sender, created, action FROM quarantine"  # noqa: S608
            f' WHERE notified = 0 AND rcpt = "{rcpt}" AND score < {max_score:f} AND (action = "{category}" OR "all" ='
            f' "{category}")'
        )
        print("%s: %d of %d messages qualify for notification" % (rcpt, len(meta_query), msg_count))
        if len(meta_query) == 0:
            return
        msg_count = len(meta_query)
        if r.get("Q_HTML"):
            template = Template(r.get("Q_HTML"))
        else:
            with open("/templates/quarantine.tpl") as f:
                template = Template(f.read())
        html = template.render(
            meta=meta_query, username=rcpt, counter=msg_count, hostname=mail_hostname, quarantine_acl=quarantine_acl
        )
        text = html2text.html2text(html)
        count = 0
        while count < 15:
            count += 1
            try:
                server = smtplib.SMTP("postfix", 590, "quarantine")
                server.ehlo()
                msg = MIMEMultipart("alternative")
                msg_from = r.get("Q_SENDER") or "quarantine@localhost"
                # Remove non-ascii chars from field
                msg["From"] = "".join([i if ord(i) < 128 else "" for i in msg_from])
                msg["Subject"] = r.get("Q_SUBJ") or "Spam Quarantine Notification"
                msg["Date"] = formatdate(localtime=True)
                text_part = MIMEText(text, "plain", "utf-8")
                html_part = MIMEText(html, "html", "utf-8")
                msg.attach(text_part)
                msg.attach(html_part)
                msg["To"] = str(rcpt)
                bcc = r.get("Q_BCC") or ""
                redirect = r.get("Q_REDIRECT") or ""
                text = msg.as_string()
                if bcc == "":
                    if redirect == "":
                        server.sendmail(msg["From"], str(rcpt), text)
                    else:
                        server.sendmail(msg["From"], str(redirect), text)
                else:
                    if redirect == "":
                        server.sendmail(msg["From"], [str(rcpt)] + [str(bcc)], text)
                    else:
                        server.sendmail(msg["From"], [str(redirect)] + [str(bcc)], text)
                server.quit()
                for res in meta_query:
                    query_mysql(
                        'UPDATE quarantine SET notified = 1 WHERE id = "%d"' % (res["id"]),  # noqa: S608
                        update=True,
                    )
                r.hset("Q_LAST_NOTIFIED", record["rcpt"], time_now)
                break
            except Exception as ex:
                server.quit()
                print("%s" % (ex))
                time.sleep(3)

    records = query_mysql(
        "SELECT IFNULL(user_acl.quarantine, 0) AS quarantine_acl, count(id) AS counter, rcpt FROM quarantine LEFT OUTER"  # noqa: S608
        " JOIN user_acl ON user_acl.username = rcpt WHERE notified = 0 AND score < %f AND rcpt in (SELECT username FROM"
        " mailbox) GROUP BY rcpt" % (max_score)
    )

    for record in records:
        attrs = ""
        attrs_json = ""
        time_trans = {"hourly": 3600, "daily": 86400, "weekly": 604800}
        try:
            last_notification = int(r.hget("Q_LAST_NOTIFIED", record["rcpt"]))
            if last_notification > time_now:
                print("Last notification is > time now, assuming never")
                last_notification = 0
        except Exception:
            print("Could not determine last notification for %s, assuming never" % (record["rcpt"]))
            last_notification = 0
        attrs_json = query_mysql('SELECT attributes FROM mailbox WHERE username = "%s"' % (record["rcpt"]))  # noqa: 608
        attrs = attrs_json[0]["attributes"]
        attrs = json.loads(attrs) if isinstance(attrs, str) else json.loads(attrs.decode("utf-8"))
        if attrs["quarantine_notification"] not in ("hourly", "daily", "weekly"):
            continue
        if last_notification == 0 or (last_notification + time_trans[attrs["quarantine_notification"]]) <= time_now:
            print(
                "Notifying %s: Considering %d new items in quarantine (policy: %s)"
                % (record["rcpt"], record["counter"], attrs["quarantine_notification"])
            )
            notify_rcpt(record["rcpt"], record["counter"], record["quarantine_acl"], attrs["quarantine_category"])

finally:
    os.unlink(pidfile)
