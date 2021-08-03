#!/bin/bash

echo "AccountID $MAXMIND_USER_ID" >> /usr/local/etc/GeoIP.conf
echo "LicenseKey $MAXMIND_LICENSE_KEY" >> /usr/local/etc/GeoIP.conf
geoipupdate

echo "Collecting static files"
python manage.py collectstatic --no-input

echo "Initialize application"
python scripts/init.py &

echo "start nginx service"
service nginx start

echo "Adding jobs to crontab"
# Add cronjobs to crontab
python manage.py crontab add

# Copy environment variables into environment
# so that cron jobs can access
echo "$(env ; crontab -l)" | crontab -

# Start cron service
service cron start

echo "Starting Con-PCA API"
if [[ $DEBUG -eq 1 ]]
then
  echo "Run server"
  if [[ $PROFILE -eq 1 ]]
  then
    mkdir /tmp
    mkdir /tmp/profile-data
    python manage.py runprofileserver --use-cprofile --prof-path=/tmp/profile-data
  else
    python manage.py runserver 0.0.0.0:8000
  fi
else
  echo "Serve using WSGI"
  gunicorn --workers="$WORKERS" --bind=0.0.0.0:8000 --timeout 600 config.wsgi
fi
