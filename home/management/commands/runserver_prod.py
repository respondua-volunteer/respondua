# your_app/management/commands/runserver_debug.py
from django.core.management.commands.runserver import Command as RunserverCommand
import os
from pathlib import Path
from decouple import config
from django.conf.urls.static import static



class Command(RunserverCommand):
    def handle(self, *args, **options):
        from django.conf import settings

        settings.DEBUG = False

        # aws settings
        settings.AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        settings.AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        settings.AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
        settings.DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' 
        settings.AWS_S3_CUSTOM_DOMAIN = 'd20h3k8rvqrkq4.cloudfront.net'
        settings.AWS_LOCATION = 'static'
        settings.STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        settings.STATIC_URL = 'https://%s/%s/' % (settings.AWS_S3_CUSTOM_DOMAIN, settings.AWS_LOCATION)  

        # DATABASES settings
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': config('POSTGRES_DB','postgres'),
                'USER': config('POSTGRES_USER','postgres'),
                'PASSWORD': config('POSTGRES_PASSWORD','postgres'),
                'HOST': config('POSTGRES_HOST','localhost'),
                'PORT': config('POSTGRES_PORT', 5432)
            }
        }

        # Redis settings
        settings.REDIS_HOST = config('REDIS_HOST', '127.0.0.1')
        settings.REDIS_PORT = config('REDIS_PORT', '6379')
        settings.CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
                "OPTIONS": {
                    "db": 0,
                    "parser_class": "redis.connection.PythonParser",
                    "pool_class": "redis.BlockingConnectionPool",
            
                }
            }
        }

        print("Original INSTALLED_APPS:", settings.INSTALLED_APPS)
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'debug_toolbar']
        settings.MIDDLEWARE = [app for app in settings.MIDDLEWARE if app != 'debug_toolbar.middleware.DebugToolbarMiddleware']
        print("Modified INSTALLED_APPS:", settings.INSTALLED_APPS)




        super().handle(*args, **options)
