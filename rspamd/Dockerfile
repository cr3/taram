ARG DEBIAN_RELEASE=bookworm
FROM debian:${DEBIAN_RELEASE}-slim

ARG DEBIAN_RELEASE
ARG DEBIAN_FRONTEND=noninteractive
ARG RSPAMD_VER=rspamd_3.11.0-1~90a175b45
ENV LC_ALL=C

RUN apt-get update && apt-get install -y \
  tzdata \
  ca-certificates \
  gnupg2 \
  dnsutils \
  netcat-traditional \
  wget \
  redis-tools \ 
  procps \ 
  && arch=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) \
  && wget -P /tmp https://rspamd.com/apt-stable/pool/main/r/rspamd/${RSPAMD_VER}~${DEBIAN_RELEASE}_${arch}.deb \
  && apt install -y /tmp/${RSPAMD_VER}~${DEBIAN_RELEASE}_${arch}.deb \
  && rm -rf /var/lib/apt/lists/* /tmp/* \
  && apt-get autoremove --purge \
  && apt-get clean \
  && mkdir -p /run/rspamd \
  && chown _rspamd:_rspamd /run/rspamd \
  && sed -i 's/#analysis_keyword_table > 0/analysis_cat_table.macro_exist == "M"/g' /usr/share/rspamd/lualib/lua_scanners/oletools.lua

COPY settings.conf /etc/rspamd/
COPY lua /etc/rspamd/lua
COPY local.d /etc/rspamd/local.d
COPY override.d /etc/rspamd/override.d

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

STOPSIGNAL SIGTERM

EXPOSE 11332 11333 11334

CMD ["/usr/bin/rspamd", "-f", "-u", "_rspamd", "-g", "_rspamd"]
