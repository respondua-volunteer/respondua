from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Event


class EventAdmin(TranslatableAdmin):
    list_display = ('title', 'description', 'place',)
    fields = ('title', 'description', 'place', 'date', 'time', 'image')

admin.site.register(Event, EventAdmin)