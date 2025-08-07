import os
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime, timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")  # или dev

# Основные настройки
bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = 30
graceful_timeout = 30
keepalive = 5

# Логирование
loglevel = os.getenv("LOGLEVEL", "info")
accesslog = '-'  # stdout
errorlog = '-'   # stderr

# JSON форматтер
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Удаляем старое поле
        log_record.pop('timestamp', None)

        # Добавляем стандартное поле для времени
        log_record['@timestamp'] = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()

        # Приводим уровень к верхнему регистру
        log_record['level'] = (log_record.get('level') or record.levelname).upper()
        
        # log_record["app"] = "respondua"
        # log_record["env"] = os.getenv("ENV", "dev")
        # log_record["service"] = "volunteer"

def post_fork(server, worker):
    import logging

    formatter = CustomJsonFormatter(
        fmt='%(timestamp)f %(level)8s %(name)s %(message)s',
    )

    # Настройка для error логов
    error_logger = logging.getLogger('gunicorn.error')
    for h in error_logger.handlers:
        h.setFormatter(formatter)

    # Настройка для access логов
    access_logger = logging.getLogger('gunicorn.access')
    for h in access_logger.handlers:
        h.setFormatter(formatter)

    app_logger = logging.getLogger('app')
    if not app_logger.handlers:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        app_logger.addHandler(stream_handler)
        app_logger.setLevel(loglevel.upper())
