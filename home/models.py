from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Event(TranslatableModel):
    image = models.ImageField(upload_to='images/', default=None)
    date = models.DateField(default=None, null=True, blank=True)
    time = models.TimeField(default=None, null=True, blank=True)
    translations = TranslatedFields(
        title = models.CharField(max_length=200),
        description = models.TextField(),
        place = models.CharField(max_length=200, null=True, blank=True)
    )

    def __str__(self):
        return self.title
