from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListCreateView.as_view(), name="list-create"),
    path("<uuid:pk>/", views.ProjectDetailView.as_view(), name="detail"),
]
