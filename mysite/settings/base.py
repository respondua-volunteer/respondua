import os
import django
from pathlib import Path
from decouple import config
from django.utils.encoding import smart_str

django.utils.encoding.smart_text = smart_str

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

CSRF_TRUSTED_ORIGINS = ['https://*.respondua.org']

INSTALLED_APPS = [
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
    'rest_framework_swagger',
    'rest_framework',
    'drf_yasg',
    'debug_toolbar',
]

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
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [BASE_DIR / 'staticfiles']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor 5 Config
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'link', '|',
            'code', 'codeBlock', 'insertImage', 'insertTable', 'horizontalLine', '|',
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
                {'language': 'python', 'label': 'Python'},
                {'language': 'html', 'label': 'HTML'},
                {'language': 'css', 'label': 'CSS'},
                {'language': 'javascript', 'label': 'JavaScript'},
            ]
        },
        'language': 'en',
    }
}


# LiqPay
LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY", default="sandbox_i97618994403")
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY", default="sandbox_997Trh...")
LIQPAY_SANDBOX_MODE = config("LIQPAY_SANDBOX_MODE", default=True, cast=bool)

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
