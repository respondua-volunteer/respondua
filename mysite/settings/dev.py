from .base import *

DEBUG = True

ALLOWED_HOSTS=['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")


DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", "VIDGUK <no-reply@respondua.org>")
CONTACT_EMAIL = config("CONTACT_EMAIL", "charityfound@respondua.org")
DONATIONS_BCC = [e for e in config("DONATIONS_BCC", "").split(",") if e]


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(config("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "yourgmail@gmail.com")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "<app-password>")
EMAIL_TIMEOUT = 30
SERVER_EMAIL = DEFAULT_FROM_EMAIL

