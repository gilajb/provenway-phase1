from django.urls import path

from . import views

app_name = "directory"

urlpatterns = [
    path("", views.DirectorySearchView.as_view(), name="search"),
]
