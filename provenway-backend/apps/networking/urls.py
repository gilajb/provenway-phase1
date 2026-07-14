from django.urls import path

from . import views

app_name = "networking"

urlpatterns = [
    path("<uuid:user_id>/follow/", views.FollowToggleView.as_view(), name="follow"),
    path(
        "<uuid:user_id>/followers/", views.FollowersListView.as_view(), name="followers"
    ),
    path(
        "<uuid:user_id>/following/", views.FollowingListView.as_view(), name="following"
    ),
    path(
        "<uuid:user_id>/follow-status/",
        views.FollowStatusView.as_view(),
        name="follow-status",
    ),
]
