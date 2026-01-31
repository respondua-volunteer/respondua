#!/bin/sh

echo "Using settings: $DJANGO_SETTINGS_MODULE"

echo "Applying database migrations..."
python manage.py migrate --noinput


exec gunicorn -c gunicorn.conf.py mysite.wsgi:application