from django.contrib import admin
from .models import Post, Profile
from tinymce.widgets import TinyMCE
from django.db import models 


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    # formfield_overrides = {
    #     models.TextField: {'widget': TinyMCE()},
    # }

admin.site.register(Post, PostAdmin)
admin.site.register(Profile)