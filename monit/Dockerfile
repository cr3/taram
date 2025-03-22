FROM debian:bookworm-slim

RUN apt update && apt install -y \
    curl \
    bind9-dnsutils \
    jq \
    monitoring-plugins-standard \
    monit \
    redis-tools

COPY --chmod=600 monitrc /etc/monit/monitrc
COPY conf /etc/monit/conf-enabled
COPY scripts /opt/monit/scripts

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["monit", "-I", "-B"]
