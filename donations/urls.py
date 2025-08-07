from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("donations/export/", views.export_all_csv, name="export_all_csv"),
]
