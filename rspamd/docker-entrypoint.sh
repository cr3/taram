#!/bin/bash

echo ${IPV4_NETWORK}.0/24 > /etc/rspamd/custom/mail_networks.map
echo ${IPV6_NETWORK} >> /etc/rspamd/custom/mail_networks.map

DOVECOT_V4=
DOVECOT_V6=
until [[ ! -z ${DOVECOT_V4} ]]; do
  DOVECOT_V4=$(dig a dovecot +short)
  DOVECOT_V6=$(dig aaaa dovecot +short)
  [[ ! -z ${DOVECOT_V4} ]] && break;
  echo "Waiting for Dovecot..."
  sleep 3
done
echo ${DOVECOT_V4}/32 > /etc/rspamd/custom/dovecot_trusted.map
if [[ ! -z ${DOVECOT_V6} ]]; then
  echo ${DOVECOT_V6}/128 >> /etc/rspamd/custom/dovecot_trusted.map
fi

RSPAMD_V4=
RSPAMD_V6=
until [[ ! -z ${RSPAMD_V4} ]]; do
  RSPAMD_V4=$(dig a rspamd +short)
  RSPAMD_V6=$(dig aaaa rspamd +short)
  [[ ! -z ${RSPAMD_V4} ]] && break;
  echo "Waiting for Rspamd..."
  sleep 3
done
echo ${RSPAMD_V4}/32 > /etc/rspamd/custom/rspamd_trusted.map
if [[ ! -z ${RSPAMD_V6} ]]; then
  echo ${RSPAMD_V6}/128 >> /etc/rspamd/custom/rspamd_trusted.map
fi

if [[ ! -z ${REDIS_SLAVEOF_IP} ]]; then
  cat <<EOF > /etc/rspamd/local.d/redis.conf
read_servers = "redis:6379";
write_servers = "${REDIS_SLAVEOF_IP}:${REDIS_SLAVEOF_PORT}";
password = "${REDISPASS}";
timeout = 10;
EOF
  until [[ $(redis-cli -h redis -a ${REDISPASS} --no-auth-warning PING) == "PONG" ]]; do
    echo "Waiting for Redis @redis..."
    sleep 2
  done
  until [[ $(redis-cli -h ${REDIS_SLAVEOF_IP} -p ${REDIS_SLAVEOF_PORT} -a ${REDISPASS} --no-auth-warning PING) == "PONG" ]]; do
    echo "Waiting for Redis @${REDIS_SLAVEOF_IP}..."
    sleep 2
  done
  redis-cli -h redis -a ${REDISPASS} --no-auth-warning SLAVEOF ${REDIS_SLAVEOF_IP} ${REDIS_SLAVEOF_PORT}
else
  cat <<EOF > /etc/rspamd/local.d/redis.conf
servers = "redis:6379";
password = "${REDISPASS}";
timeout = 10;
EOF
  until [[ $(redis-cli -h redis -a ${REDISPASS} --no-auth-warning PING) == "PONG" ]]; do
    echo "Waiting for Redis slave..."
    sleep 2
  done
  redis-cli -h redis -a ${REDISPASS} --no-auth-warning SLAVEOF NO ONE
fi

# Provide additional lua modules
chmod 755 /var/lib/rspamd
chown -R _rspamd:_rspamd /var/lib/rspamd

exec "$@"
