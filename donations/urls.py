from django.urls import path
from . import views
from .views import test_log_view

urlpatterns = [
    path("create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("donations/export/", views.export_all_csv, name="export_all_csv"),
    path("test-log/", test_log_view),
]
