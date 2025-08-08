# gunicorn.conf.py
import os
import sys
import logging
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger

# Если не задано извне — используем dev
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")

# ---------- Gunicorn core ----------
bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = 30
graceful_timeout = 30
keepalive = 5

# ---------- Logging ----------
loglevel = os.getenv("LOGLEVEL", "info")
accesslog = "-"   # stdout
errorlog  = "-"   # stderr
# уберём цветные логи, чтобы не было мусора в JSON
enable_stdio_inheritance = True

# Access в key=value — Promtail легко разберёт через logfmt
# D = duration(μs), r=request line, s=status, b=bytes, f=referer, a=user-agent
access_log_format = (
    'remote_addr=%(h)s '
    'request="%(r)s" '
    'status=%(s)s '
    'bytes=%(b)s '
    'referer="%(f)s" '
    'user_agent="%(a)s" '
    'duration_us=%(D)s'
)

# ---------- JSON formatter ----------
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        # базовые поля
        super().add_fields(log_record, record, message_dict)

        # вычищаем возможные legacy-поля
        log_record.pop("timestamp", None)
        log_record.pop("asctime", None)

        # единый UTC-таймстемп для Loki
        log_record["@timestamp"] = datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).isoformat()

        # нормализуем уровень и имя логгера
        log_record["level"] = (log_record.get("level") or record.levelname).upper()
        log_record["logger"] = log_record.get("logger") or record.name

        # можно добавить контекст окружения (опционально)
        svc = os.getenv("SERVICE_NAME")
        env = os.getenv("ENV")
        if svc:
            log_record["service"] = svc
        if env:
            log_record["env"] = env

def _install_json_formatter(logger: logging.Logger, stream):
    """Заменяем форматтер на чистый JSON без префиксов."""
    formatter = CustomJsonFormatter()  # без fmt -> без лишних полей
    # Обнулим хендлеры и поставим свой, чтобы не осталось старых форматтеров
    logger.handlers[:] = []
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

def post_fork(server, worker):
    # error -> stderr в JSON
    _install_json_formatter(logging.getLogger("gunicorn.error"), sys.stderr)

    # access -> stdout в JSON (message содержит key=value по access_log_format)
    _install_json_formatter(logging.getLogger("gunicorn.access"), sys.stdout)

    # пользовательский логгер приложения (на всякий)
    app_logger = logging.getLogger("app")
    if not app_logger.handlers:
        _install_json_formatter(app_logger, sys.stdout)
        app_logger.setLevel(loglevel.upper())
