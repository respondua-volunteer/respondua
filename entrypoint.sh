#!/bin/sh

echo "Using settings: $DJANGO_SETTINGS_MODULE"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 mysite.wsgi:application
