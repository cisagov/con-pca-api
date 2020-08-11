#!/bin/bash

echo "Collecting static files"
python manage.py collectstatic --no-input

echo "Initialize application"
python scripts/init.py &

echo "start nginx service"
service nginx start

if [[ $DEBUG -eq 1 ]]
then
    echo "Run server"
    python manage.py runserver 0.0.0.0:8000
else
    echo "Setup Cron"
    echo "$(env ; crontab -l)" | crontab -
    python manage.py crontab add
    service cron start

    echo "Serve using WSGI"
    gunicorn --workers=$WORKERS --bind=0.0.0.0:8000 config.wsgi
fi
