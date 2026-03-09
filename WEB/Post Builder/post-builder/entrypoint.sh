#!/bin/sh

if [ -z "$ADMIN_PASSWORD" ]; then
    export ADMIN_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32)
    echo "[*] Generated random ADMIN_PASSWORD"
fi

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
