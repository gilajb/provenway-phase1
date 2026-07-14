from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("me/", views.MyProfileView.as_view(), name="me"),
    path("me/avatar/", views.AvatarUploadView.as_view(), name="me-avatar"),
    path("<uuid:user_id>/", views.PublicProfileView.as_view(), name="public-profile"),
]
