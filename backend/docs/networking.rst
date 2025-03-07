Networking
==========

Register Domain
---------------

* https://my.ionos.com/domains

Modify DNS Settings
-------------------

* Remove all records.
* Create a CNAME with host name `_domainconnect` and value `_domainconnect.ionos.com`.

Forward ports
-------------

On the router, forward these ports to the server:

* 22 for SSH
* 80 for HTTP
* 443 for HTTPS
