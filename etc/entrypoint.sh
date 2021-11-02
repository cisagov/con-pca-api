#!/bin/bash

echo "Updating geoip database"
echo "AccountID $MAXMIND_USER_ID" >> /usr/local/etc/GeoIP.conf
echo "LicenseKey $MAXMIND_LICENSE_KEY" >> /usr/local/etc/GeoIP.conf
geoipupdate

echo "Starting Con-PCA API"
# run flask
if [[ $DEBUG -eq 1 ]]; then
  echo "Debug Mode"
  python landing/wsgi.py &
  python api/wsgi.py
else
  echo "Serve using WSGI"
  gunicorn --workers="$WORKERS" --preload --bind=0.0.0.0:5000 --timeout=180 api.wsgi:app &
  gunicorn --workers="$WORKERS" --preload --bind=0.0.0.0:8000 --timeout=180 landing.wsgi:app
fi
