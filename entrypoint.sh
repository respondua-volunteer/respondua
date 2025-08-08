#!/bin/sh

echo "Using settings: $DJANGO_SETTINGS_MODULE"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec gunicorn -c gunicorn.conf.py mysite.wsgi:application