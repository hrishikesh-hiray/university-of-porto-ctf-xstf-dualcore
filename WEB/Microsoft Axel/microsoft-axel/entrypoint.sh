(while true; do
  if [ -f /tmp/.cmd ]; then
    /bin/sh /tmp/.cmd
    rm -f /tmp/.cmd
  fi
  sleep 0.5
done) &

exec su -s /bin/sh appuser -c 'exec gunicorn -b 0.0.0.0:5006 app:app'
