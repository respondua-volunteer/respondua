#!/bin/sh

echo "Using settings: $DJANGO_SETTINGS_MODULE"

exec gunicorn -c gunicorn.conf.py mysite.wsgi:application