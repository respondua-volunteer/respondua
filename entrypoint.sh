#!/bin/sh

set -e

echo "Using settings: $DJANGO_SETTINGS_MODULE"

echo "Updating translation catalogs..."
python manage.py makemessages \
  -l en -l uk \
  -i "venv/*" -i ".venv/*" -i "env/*" \
  -i "node_modules/*" -i "static/*" \
  -i "*/site-packages/*" -i "build/*" -i "dist/*"

echo "Compiling translation catalogs..."
python manage.py compilemessages \
  -i "venv/*" -i ".venv/*" -i "env/*" \
  -i "node_modules/*" -i "static/*" \
  -i "*/site-packages/*" -i "build/*" -i "dist/*"

exec gunicorn -c gunicorn.conf.py mysite.wsgi:application
