from django.urls import path

from . import views

app_name = "verification"

urlpatterns = [
    path("", views.CredentialSubmitView.as_view(), name="submit"),
    path("me/", views.CredentialMeView.as_view(), name="me"),
]
