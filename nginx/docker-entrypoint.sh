#!/bin/sh

until ping sogo -c1 > /dev/null; do
  echo "Waiting for SOGo..."
  sleep 1
done
until ping rspamd -c1 > /dev/null; do
  echo "Waiting for Rspamd..."
  sleep 1
done

python3 /bootstrap.py

exec "$@"
