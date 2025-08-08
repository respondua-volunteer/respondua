import os
import sys
import logging
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")

bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = 30
graceful_timeout = 30
keepalive = 5

loglevel = os.getenv("LOGLEVEL", "info")
accesslog = "-"   # stdout
errorlog  = "-"   # stderr

access_log_format = (
    'remote_addr=%(h)s '
    'request="%(r)s" '
    'status=%(s)s '
    'bytes=%(b)s '
    'referer="%(f)s" '
    'user_agent="%(a)s" '
    'duration_us=%(D)s'
)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["@timestamp"] = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        log_record["level"] = (log_record.get("level") or record.levelname).upper()
        log_record["logger"] = record.name

def post_fork(server, worker):
    json_formatter = CustomJsonFormatter(fmt="%(level)s %(logger)s %(message)s")

    err = logging.getLogger("gunicorn.error")
    for h in err.handlers:
        h.setFormatter(json_formatter)

    app_logger = logging.getLogger("app")
    if not app_logger.handlers:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(json_formatter)
        app_logger.addHandler(sh)
        app_logger.setLevel(loglevel.upper())

    acc = logging.getLogger("gunicorn.access")
    for h in acc.handlers:
        h.setFormatter(logging.Formatter("%(message)s"))
