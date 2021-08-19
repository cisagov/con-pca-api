#!/bin/bash
echo "Starting Con-PCA API"
# run flask
if [[ $DEBUG -eq 1 ]]
then
  echo "Debug Mode"
  python api/main.py &
  python landing/main.py
else
  echo "Serve using WSGI"
  gunicorn --workers="$WORKERS" --bind=0.0.0.0:5000 --timeout=180 api.wsgi:app &
  gunicorn --workers="$WORKERS" --bind=0.0.0.0:8000 --timeout=180 landing.wsgi:app
fi
