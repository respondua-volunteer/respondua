
import os
from pathlib import Path
from decouple import config

# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

import django
from django.utils.encoding import smart_str

django.utils.encoding.smart_text = smart_str

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CSRF_TRUSTED_ORIGINS=['https://*.respondua.org']



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h$q6n=l#p&5vt8$49i9&rma5(l3)h-86e*go!g1eficj-nt(c1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1','localhost','3.69.216.243','respondua.org','volunteer']


# Application definition
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
    'tinymce',
    'storages',
    'ckeditor',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates/')], 
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

INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', 'localhost',)

def show_toolbar(request):                                    
    return True                                               

DEBUG_TOOLBAR_CONFIG = {                                      
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,                    
}                                                             

if DEBUG:                                                     
    import mimetypes                                               
    mimetypes.add_type("application/javascript", ".js", True) 

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

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


# Cache time to live is 3 minutes.
CACHE_TTL = 60 * 3


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# STATICFILES_DIRS = [BASE_DIR / "static"]  
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# STATIC_URL = '/static/'   
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# # All settings common to all environments
# PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles',
]

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"




# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'uk' 

LANGUAGES = [
    ('uk', 'Ukraine'),
    ('en', 'English'),
]

TIME_ZONE = 'UTC'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'blog', 'locale'),
    os.path.join(BASE_DIR, 'home','locale'),
)

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



LIQPAY_PUBLIC_KEY = 'sandbox_i97618994403' #config('YOUR_PUBLIC_KEY')
LIQPAY_PRIVATE_KEY = 'sandbox_997Trh625acVmzO9c2Syd5EGA7D31eTQDgfYuufG' #config('YOUR_PRIVATE_KEY')
LIQPAY_SANDBOX_MODE = True  # Установите в True для тестирования в режиме песочницы (sandbox mode)


TINYMCE_JS_ROOT = os.path.join(BASE_DIR, '/mysite/static/tinymce')

TINYMCE_DEFAULT_CONFIG = {

   'height': 360,
   'width': 750,
   'cleanup_on_startup': True,
   'custom_undo_redo_levels': 20,
   'selector': 'textarea',
#    'theme': 'modern',
   'plugins': '''
   textcolor save link image media preview codesample contextmenu
   table code lists fullscreen insertdatetime nonbreaking
   contextmenu directionality searchreplace wordcount visualblocks
   visualchars code fullscreen autolink lists charmap print hr
   anchor pagebreak
   ''',
   'toolbar1': '''
   fullscreen preview bold italic underline | fontselect,
   fontsizeselect | forecolor backcolor | alignleft alignright |
   aligncenter alignjustify | indent outdent | bullist numlist table |
   | link image media | codesample |
   ''',
   'toolbar2': '''
   visualblocks visualchars |
   charmap hr pagebreak nonbreaking anchor | code |
   ''',
#    "images_upload_url": "upload_image",
   'contextmenu': 'formats | link image',
   'menubar': True,
   'statusbar': True,
   }



PARLER_LANGUAGES = {
    None: (
        {'code': 'en',}, 
        {'code': 'uk',}
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}

# sentry_sdk.init(
#     dsn="https://2ce82054ce9a13f35a9fe12cc1053c5c@o4506203313209344.ingest.sentry.io/4506203314520064",
#     integrations=[
#         DjangoIntegration(
#             transaction_style='url',
#             middleware_spans=True,
#             signals_spans=False,
#             cache_spans=False,
#         ),
#     ],
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )