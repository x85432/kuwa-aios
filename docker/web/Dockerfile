FROM nginxproxy/nginx-proxy:1.6-alpine

RUN apk update && apk --no-cache add curl dnsmasq

COPY docker/web/vhost.d/ /etc/nginx/vhost.d/

WORKDIR /app
COPY docker/web/nginx-proxy/ /app/
COPY --from=kuwaai/multi-chat:latest /app/public /app/public
RUN chown -R nginx:nginx /app

ENV DEFAULT_ROOT=none