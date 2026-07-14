from django.urls import path

from . import views

app_name = "feed"

urlpatterns = [
    path("", views.FeedListView.as_view(), name="feed-list"),
    # /feed/discover/ and /feed/trending/ (Engineering Doc §5.2) are
    # future sessions — deliberately not added here yet.
]
