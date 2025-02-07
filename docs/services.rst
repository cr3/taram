Services
========

Backend
-------

The Backend is a RESTful API that provides a programmatic way to manage
mail server functionalities. Here’s why it’s useful:

* **Automation**

  The RESTful API allows system administrators to automate tasks like
  creating mailboxes, managing domains, setting up aliases, configuring
  DKIM, and more.

* **Integration**

  The API enables integration with other systems, like web interface.

* **Scalability and Flexibility**

  When managing multiple instances or a complex infrastructure, using
  the API simplifies operations by providing a consistent and predictable
  way to execute tasks.

In short, the Backend exists to make it easier to manage and extend its
functionality in flexible and efficient ways.

ClamAV
------

`ClamAV`_ (Clamd) is the antivirus scanner to enhance the security of
the mail server by detecting and blocking malicious emails. Here's why
Clamd is integrated into the system:

* **Email Virus Scanning**

  Clamd scans incoming and outgoing emails for viruses, malware, and
  other malicious content. It helps prevent harmful attachments from
  being delivered to users' inboxes, protecting both the mail server
  and end-users.

* **Integration with Spam Filtering**

  Works alongside spam filtering systems (like Rspamd) to ensure emails
  are checked for both spam and viruses. This dual-layer security helps
  maintain the integrity of the email system.

* **Real-Time Protection**

  Operates in real-time, scanning email attachments and embedded links
  as they are processed. This immediate detection helps stop malware
  before it spreads or affects other systems.

* **Low Resource Usage**

  Lightweight and optimized for performance, making it suitable for
  integration with a Docker-based mail server without imposing significant
  resource overhead.

* **Community Support and Regular Updates**

  Widely used and regularly updated, ensuring it stays effective against
  the latest viruses, malware, and other email-based threats.

In summary, Clamd provides real-time virus scanning, enhance email
security, and protect users from potential threats delivered via email
attachments or links.

.. _ClamAV: https://www.clamav.net/

DockerAPI
---------

The DockerAPI is used in containerized environments to interact with and
manage Docker services programmatically. It serves several purposes:

* **Container Management**

  Enables starting, stopping, and restarting containers efficiently,
  automating service management.

* **Resource Monitoring**

  Tracks resource usage such as CPU, memory, and disk across containers
  to ensure smooth operation and diagnose performance issues.

* **Access Control**

  Ensures the DockerAPI is only accessible locally or over a secure,
  trusted network.

DockerAPI acts as the central mechanism for automating and orchestrating
container operations in a controlled, and secure manner.

Dovecot
-------

`Dovecot`_ is an IMAP and POP3 server which is responsible for handling
email retrieval by clients. Here’s why Dovecot is used:

* **Secure Email Access**

  Allows users to access their mailboxes securely via IMAP, IMAPS, POP3, and POP3S.

* **High Performance**

  Optimized for speed and efficiency, making it ideal for handling large
  volumes of email.

* **Authentication Management**

  Integrates with other authentication system, ensuring secure login
  with various mechanisms (e.g., SQL, LDAP, OAuth2).

* **Mailbox Storage**

  Manages and indexes Maildir storage, allowing for fast email retrieval.

* **Sieve Filtering**

  Supports Sieve for server-side email filtering, allowing users to set
  up auto-responses, sorting rules, and spam handling.

* **Integration with Other Services**

  Works closely with Postfix (SMTP server) and Rspamd (spam filtering)
  to provide a full-featured mail system.

Overall, Dovecot ensures a smooth and secure email retrieval experience.

.. _Dovecot: https://www.dovecot.org/

Memcached
---------

`Memcached`_ is used as a caching layer to improve performance and reduce
database load. Here’s why it’s included:

* **Reduced Database Load**

  Frequently accessed data, such as authentication tokens and user session
  details, are cached in Memcached instead of repeatedly querying MySQL.

* **Postfix & Dovecot Integration**

  Some email-related operations, like authentication caching, benefit
  from Memcached, improving email processing efficiency.

Overall, Memcached helps optimize performance by reducing the need for
repeated database queries and speeding up email operations.

.. _Memcached: https://memcached.org/

Monit
-----

`Monit`_ is used to ensure the reliability and availability of its
services. Here's why it's important:

* **Service Monitoring**

  Continuously monitors the health and status of critical services (like
  the mail server, databases, and web interface). If any service fails
  or becomes unresponsive, Monit can take action to restart or recover it.

* **Automated Recovery**

  If a container or service crashes, restarts it automatically. This
  minimizes downtime and ensures that the mail server stays operational
  without requiring manual intervention.

* **Preventing Downtime**

  By proactively monitoring the system, helps prevent service
  interruptions, ensuring that any issues are detected and addressed as
  soon as they occur.

* **Error Detection**

  Detects misconfigurations or errors in the Docker containers and helps
  to maintain the proper functioning of the entire mail server stack.

In summary, Monit enhances reliability, automated recovery, and service
uptime, ensuring the mail server remains resilient and functional.

.. _Monit: https://mmonit.com/monit/

Postfix
-------

`Postfix`_ is a Mail Transfer Agent (MTA) for handling email delivery
and relay. Here’s why Postfix is chosen and how it fits into the
architecture:

* **Reliable and Secure MTA**

  Widely used, battle-tested MTA known for its security, performance,
  and reliability. It has built-in protections against spam and abuse,
  making it a solid choice for a modern mail server.

* **Handling Incoming and Outgoing Mail**

  Receives emails from the internet (SMTP) and passes them to Dovecot
  for mailbox storage. Sends emails from local mailboxes to external
  recipients (SMTP relay).

* **Integration with Other Services**

  Hands off mail to Dovecot for storage and retrieval. Routes emails
  through Rspamd for spam and virus filtering. When users send emails
  via SOGo, ensures they are delivered correctly.

* **Performance and Queue Management**

  Optimized for handling high email volumes efficiently. Queues messages
  properly and retries delivery in case of temporary failures.

* **Support for TLS and Encryption**

  Configured with TLS encryption for secure email transmission. Also
  supports authentication mechanisms like SPF, DKIM, and DMARC for
  email security.

.. _Postfix: https://www.postfix.org/

Rspamd
------

`Rspamd`_ is the primary spam filtering solution to protect the mail
server and users from unwanted or malicious emails. Here's why Rspamd
is chosen:

* **Efficient Spam Filtering**

  Uses a variety of methods (such as Bayesian filtering, DNS-based
  blacklists (RBLs), DKIM, DMARC, and SPF checks) to accurately classify
  emails as spam or legitimate. This reduces the chances of spam slipping
  through to users’ inboxes.

* **Performance and Speed**

  Known for its high performance and low resource consumption, making
  it well-suited for use in a dockerized environment where resource
  efficiency is important.

* **Customizable and Flexible**

  Offers extensive configuration options, allowing for tailored spam
  filtering rules, custom scoring, and integration with other services
  like ClamAV for virus scanning or external RBLs for additional spam
  detection.

* **Advanced Features**

  Includes advanced features like learning filters, graylisting, and
  multi-threaded processing, which enhance the accuracy of spam detection
  and reduce false positives.

* **Integration with DKIM, DMARC, and SPF**

  Checks for authentication failures using DKIM, DMARC, and SPF records,
  helping to detect phishing or spoofed emails and ensure legitimate
  senders.

* **Real-Time Processing**

  Processes emails in real time, ensuring that incoming and outgoing
  emails are checked as soon as they are received, minimizing the risk
  of malicious content or spam affecting the system.

In summary, Rspamd is used for its efficiency, advanced spam filtering
capabilities, and ability to integrate with other security systems like
ClamAV, providing a comprehensive and flexible anti-spam solution.

.. _Rspamd: https://rspamd.com/

Unbound
-------

`Unbound`_ is a high-performance, open-source DNS resolver designed for
privacy, security, and speed. It resolves domain names into IP addresses,
and caches results for faster responses. Here's why it's used:

* **Privacy Protection**

  Ensures DNS queries are resolved securely without relying on
  external DNS providers, reducing exposure of sensitive metadata like
  email-related DNS lookups (e.g., MX, SPF, DKIM, DMARC records).

* **DNSSEC Validation**

  Validates DNS responses using DNSSEC, ensuring the integrity and
  authenticity of DNS records, which is critical to preventing attacks
  like DNS spoofing or cache poisoning.

* **Performance Improvement**

  Caches DNS queries, significantly reducing response times for repeated
  lookups and optimizing the performance of services like spam filtering
  (which rely on frequent DNS lookups).

* **Integration with Mail Services**

  Email servers frequently query DNS to verify sender domains, validate
  email authenticity (e.g., SPF, DKIM, DMARC checks), and handle spam
  filtering (via RBLs). Unbound ensures these lookups are fast, reliable,
  and secure.

* **Resilience and Control**

  Ensures operations are independent of external DNS providers, increasing
  reliability and control in case of outages or misconfigurations with
  upstream DNS.

* **Enhanced Security for Anti-Spam**

  Strengthens the security of DNS lookups used by spam filters (e.g.,
  ClamAV, Rspamd) to block spam and phishing emails, making the mail
  server more robust.

In short, Unbound ensures faster, more secure, and private DNS resolution,
which is essential for running a reliable and secure mail server.

.. _Unbound: https://nlnetlabs.nl/projects/unbound/about/
