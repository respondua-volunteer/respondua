# your_app/management/commands/runserver_dev.py
from django.core.management.commands.runserver import Command as RunserverCommand
import os
from pathlib import Path
from decouple import config
from django.conf.urls.static import static
from django.conf import settings
from numpy import append



#Now isn't useful
class Command(RunserverCommand):
    def handle(self, *args, **options):

        settings.DEBUG = True


        # DATABASES settings
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': settings.BASE_DIR / 'db.sqlite3',
            }
        }


        




        super().handle(*args, **options)
