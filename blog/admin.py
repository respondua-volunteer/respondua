from django.contrib import admin
from django import forms
from .models import Post, Profile
from django_ckeditor_5.widgets import CKEditor5Widget
from modeltranslation.admin import TranslationAdmin
from modeltranslation.admin import TabbedTranslationAdmin


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "content_en": CKEditor5Widget(config_name='default'),
            "content_uk": CKEditor5Widget(config_name='default'),
        }

class PostAdmin(TabbedTranslationAdmin):
    form = PostAdminForm
    list_display = ('title', 'author', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {
        'slug_en': ('title_en',),
        'slug_uk': ('title_uk',),
    }

    class Media:
        js = TabbedTranslationAdmin.Media.js + (
            "admin/js/lang-tabs.js",
        )
        css = {
            'all': ('admin/css/post.css',)
        }


admin.site.register(Post, PostAdmin)
admin.site.register(Profile)