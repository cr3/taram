#!/bin/bash

restart_service() {
  service=$1
  echo "Restarting $service..."
  message=$(curl --silent -X POST http://dockerapi/services/${service}/restart | jq -r .message)
  if [ -z "$message" ]; then
    echo "failed connecting to dockerapi"
  else
    echo $message
  fi
}

for service in nginx dovecot postfix; do
  restart_service $service
done
