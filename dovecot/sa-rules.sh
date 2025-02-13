#!/bin/bash

# Create temp directories
[[ ! -d /tmp/sa-rules-heinlein ]] && mkdir -p /tmp/sa-rules-heinlein

# Hash current SA rules
if [[ ! -f /etc/rspamd/custom/sa-rules ]]; then
  HASH_SA_RULES=0
else
  HASH_SA_RULES=$(cat /etc/rspamd/custom/sa-rules | md5sum | cut -d' ' -f1)
fi

# Deploy
if curl --connect-timeout 15 --retry 10 --max-time 30 https://www.spamassassin.heinlein-support.de/$(dig txt 1.4.3.spamassassin.heinlein-support.de +short | tr -d '"' | tr -dc '0-9').tar.gz --output /tmp/sa-rules-heinlein.tar.gz; then
  if gzip -t /tmp/sa-rules-heinlein.tar.gz; then
    tar xfvz /tmp/sa-rules-heinlein.tar.gz -C /tmp/sa-rules-heinlein
    cat /tmp/sa-rules-heinlein/*cf > /etc/rspamd/custom/sa-rules
  fi
else
  echo "Failed to download SA rules. Exiting."
  exit 0 # Must be 0 otherwise dovecot would not start at all
fi

sed -i -e 's/\([^\\]\)\$\([^\/]\)/\1\\$\2/g' /etc/rspamd/custom/sa-rules

if [[ "$(cat /etc/rspamd/custom/sa-rules | md5sum | cut -d' ' -f1)" != "${HASH_SA_RULES}" ]]; then
  curl --silent --insecure -XPOST --connect-timeout 15 --max-time 120 https://dockerapi/services/rspamd/restart
fi

# Cleanup
rm -rf /tmp/sa-rules-heinlein /tmp/sa-rules-heinlein.tar.gz
