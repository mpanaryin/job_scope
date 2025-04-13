#!/bin/sh
set -e

# Если ENVIRONMENT не задан, считаем, что это production-режим
: "${ENVIRONMENT:=production}"

if [ "$ENVIRONMENT" = "production" ]; then
    cp /etc/nginx/nginx.prod.conf.template /etc/nginx/nginx.conf
elif [ "$ENVIRONMENT" = "testing" ]; then
    cp /etc/nginx/nginx.test.conf.template /etc/nginx/nginx.conf
else
    cp /etc/nginx/nginx.dev.conf.template /etc/nginx/nginx.conf
fi

# Подстановка переменной DOMAIN (и других, если нужно)
envsubst '$DOMAIN' < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.tmp && mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf

exec nginx -g 'daemon off;'
