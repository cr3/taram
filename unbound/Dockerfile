FROM alpinelinux/unbound

RUN apk add --update --no-cache \
  curl \
  bash \
  bind-tools \
  && install -d -g unbound -m 775 /etc/unbound

COPY docker-healthcheck.sh /
HEALTHCHECK --interval=30s --timeout=30s CMD [ "/docker-healthcheck.sh" ]

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 53/udp 53/tcp

CMD ["/usr/sbin/unbound"]
