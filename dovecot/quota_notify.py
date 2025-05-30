#!/usr/bin/python3

import contextlib
import json
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from subprocess import PIPE, STDOUT, Popen

import html2text
from jinja2 import Template

import redis

if len(sys.argv) > 2:
    percent = int(sys.argv[1])
    username = str(sys.argv[2])
else:
    print("Args missing")
    sys.exit(1)

while True:
    try:
        r = redis.StrictRedis(host="redis", decode_responses=True, port=6379, db=0)
        r.ping()
    except Exception as ex:
        print("%s - trying again..." % (ex))
        time.sleep(3)
    else:
        break

if r.get("QW_HTML"):
    template = Template(r.get("QW_HTML"))
else:
    with open("/templates/quota.tpl") as file_:
        template = Template(file_.read())

html = template.render(username=username, percent=percent)
text = html2text.html2text(html)

try:
    msg = MIMEMultipart("alternative")
    msg["From"] = r.get("QW_SENDER") or "quota-warning@localhost"
    msg["Subject"] = r.get("QW_SUBJ") or "Quota warning"
    msg["Date"] = formatdate(localtime=True)
    text_part = MIMEText(text, "plain", "utf-8")
    html_part = MIMEText(html, "html", "utf-8")
    msg.attach(text_part)
    msg.attach(html_part)
    msg["To"] = username
    p = Popen(
        [  # noqa: S603
            "/usr/libexec/dovecot/dovecot-lda",
            "-d",
            username,
            "-o",
            '"plugin/quota=maildir:User quota:noenforcing"',
        ],
        stdout=PIPE,
        stdin=PIPE,
        stderr=STDOUT,
    )
    p.communicate(input=bytes(msg.as_string(), "utf-8"))

    domain = username.split("@")[-1]
    if domain and r.hget("QW_BCC", domain):
        bcc_data = json.loads(r.hget("QW_BCC", domain))
        bcc_rcpts = bcc_data["bcc_rcpts"]
        if bcc_data["active"] == 1:
            for rcpt in bcc_rcpts:
                msg = MIMEMultipart("alternative")
                msg["From"] = username
                subject = r.get("QW_SUBJ") or "Quota warning"
                msg["Subject"] = subject + " (" + username + ")"
                msg["Date"] = formatdate(localtime=True)
                text_part = MIMEText(text, "plain", "utf-8")
                html_part = MIMEText(html, "html", "utf-8")
                msg.attach(text_part)
                msg.attach(html_part)
                msg["To"] = rcpt
                server = smtplib.SMTP("postfix", 588, "quotanotification")
                server.ehlo()
                server.sendmail(msg["From"], str(rcpt), msg.as_string())
                server.quit()

except Exception as ex:
    print("Failed to send quota notification: %s" % (ex))
    sys.exit(1)

with contextlib.suppress(Exception):
    sys.stdout.close()


with contextlib.suppress(Exception):
    sys.stderr.close()
