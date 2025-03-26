FROM alpine:3.20

RUN apk upgrade --no-cache \
  && apk add --update --no-cache \
  bash \
  curl \
  openssl \
  bind-tools \
  jq \
  mariadb-client \
  redis \
  tini \
  tzdata \
  python3 \
  acme-tiny --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community/

COPY acme.sh \
  functions.sh \
  obtain-certificate.sh \
  reload-configurations.sh \
  expand6.sh \
  /srv/

CMD ["/sbin/tini", "-g", "--", "/srv/acme.sh"]
