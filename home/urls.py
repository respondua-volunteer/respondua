from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path('team/', views.team, name='team'),
    path('privacy-policy/', views.external_privacy_policy, name='external_privacy_policy')
]