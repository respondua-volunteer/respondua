#!/bin/sh
set -euo pipefail

echo "Using settings: ${DJANGO_SETTINGS_MODULE:-mysite.settings}"

# --- i18n ---
# В проде обычно достаточно compilemessages.
# Включи makemessages, если нужно пересканировать шаблоны (DEV/одноразово):
# I18N_MAKE_MESSAGES=1
if [ "${I18N_MAKE_MESSAGES:-0}" = "1" ]; then
  echo "Running makemessages (en, uk)…"
  python manage.py makemessages \
    -l en -l uk \
    -i "venv/*" -i ".venv/*" -i "env/*" \
    -i "node_modules/*" -i "static/*" \
    -i "*/site-packages/*" -i "build/*" -i "dist/*"
fi

# Компиляция .po → .mo (по умолчанию включена, можно отключить I18N_COMPILE_MESSAGES=0)
if [ "${I18N_COMPILE_MESSAGES:-1}" = "1" ]; then
  echo "Compiling messages…"
  python manage.py compilemessages \
    -i "venv/*" -i ".venv/*" -i "env/*" \
    -i "node_modules/*" -i "static/*" \
    -i "*/site-packages/*" -i "build/*" -i "dist/*"
fi

echo "Applying database migrations…"
python manage.py migrate --noinput

echo "Collecting static files…"
python manage.py collectstatic --noinput

echo "Starting gunicorn…"
exec gunicorn -c gunicorn.conf.py mysite.wsgi:application
