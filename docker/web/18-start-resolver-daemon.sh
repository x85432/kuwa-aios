#!/bin/sh

# Use dnsmasq as resolver to resolve "host.docker.internal".
# Reference: https://github.com/NginxProxyManager/nginx-proxy-manager/issues/1225

set -e

entrypoint_log() {
    if [ -z "${NGINX_ENTRYPOINT_QUIET_LOGS:-}" ]; then
        ME=$(basename "$0")
        echo "$ME: $@"
    fi
}

# Check if dnsmasq is already running
if pgrep -f dnsmasq > /dev/null; then
  entrypoint_log "info: dnsmasq is already running."
  exit 0
fi

# Start dnsmasq as a daemon
entrypoint_log "info: Starting dnsmasq"
dnsmasq

# Check if dnsmasq started successfully
if pgrep -f dnsmasq > /dev/null; then
  entrypoint_log "info: dnsmasq started successfully."
else
  entrypoint_log "error: Failed to start dnsmasq."
  exit 1
fi