import os
import django
from pathlib import Path
from decouple import config
from django.utils.encoding import smart_str
from decouple import AutoConfig, Config, RepositoryEnv, Csv
import logging.config
from django.utils.log import DEFAULT_LOGGING

django.utils.encoding.smart_text = smart_str

BASE_DIR = Path(__file__).resolve().parent.parent.parent


ENV_FILE = config("ENV_FILE", ".env")
candidate = BASE_DIR / ENV_FILE

if candidate.exists():
    config = Config(RepositoryEnv(candidate))
else:
    config = AutoConfig(search_path=str(BASE_DIR))

# Stripe donation settings
DONATION_MIN = 1      # минимальная сумма в валюте
DONATION_MAX = None   # максимальная сумма
DONATION_CURRENCY = "pln"

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

CSRF_TRUSTED_ORIGINS = ['https://*.respondua.org']

LOGGING_CONFIG = None

LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },

    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOGLEVEL,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
        'app': {
            'handlers': ['console'],
            'level': LOGLEVEL,
            'propagate': False,
        },
        'app.donations': {
            'handlers': ['console'],
            'level': LOGLEVEL,
            'propagate': False,
        },
        'blog': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'blog.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


INSTALLED_APPS = [
    'modeltranslation',
    'django_prometheus',
    'parler',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'home',
    'taggit',
    'liqpay',
    'storages',
    'django_ckeditor_5',
    'django_extensions',
    'rest_framework',
    'drf_spectacular',
    'donations'
]

REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Respond API',
    'DESCRIPTION': 'API documentation for Respond project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX_TRIM': True,
}

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', 'localhost')

# Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')   

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor 5 Config
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'link', '|',
            'code', 'codeBlock', 'sourceEditing', '|', 
            'insertImage', 'insertTable', 'horizontalLine', '|',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'undo', 'redo'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', 'imageStyle:full', 'imageStyle:side']
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells']
        },
        'codeBlock': {
            'languages': [
                {'language': 'plaintext', 'label': 'Text'},
                {'language': 'html', 'label': 'HTML'},
            ]
        },
        'language': 'en',
    }
}



# LiqPay
LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY")
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY")
LIQPAY_SANDBOX_MODE = config("LIQPAY_SANDBOX_MODE")

# i18n / L10n
LANGUAGE_CODE = 'uk'

LANGUAGES = [
    ('uk', 'Ukrainian'),
    ('en', 'English'),
]

TIME_ZONE = 'UTC'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'blog', 'locale'),
    os.path.join(BASE_DIR, 'home', 'locale'),
]

USE_I18N = True
USE_L10N = True
USE_TZ = True

# modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = "uk"
MODELTRANSLATION_LANGUAGES = ("uk", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("uk",)

PARLER_LANGUAGES = {
    None: (
        {'code': 'en'},
        {'code': 'uk'},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHE_TTL = 60 * 3

import logging.config
logging.config.dictConfig(LOGGING)


# {container="volunteer"} |= "ERROR"
# {container="volunteer"} |= "Donation"
# {container="volunteer"} |~ "INFO|ERROR"