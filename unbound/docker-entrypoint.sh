#!/bin/bash

echo "Receiving anchor key..."
/usr/sbin/unbound-anchor -a /etc/unbound/root.key
echo "Receiving root hints..."
curl -o /etc/unbound/root.hints https://www.internic.net/domain/named.cache

exec "$@"
