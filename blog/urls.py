from . import views
from django.urls import path
from django.urls import path, include

urlpatterns = [
    path('blog/', views.PostList.as_view(), name='blog'),
    path('search/', views.search_posts, name='search_posts'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('recent_posts/', views.RecentPosts.as_view(), name='recent_posts'), 
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]