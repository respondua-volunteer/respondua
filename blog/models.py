from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field

STATUS = (
    (0, "Draft"),
    (1, "Publish")
)

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    bio = models.TextField()
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return str(self.name)

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    image = models.ImageField(upload_to='images/')
    tags = TaggableManager()
    teaser_text = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title