from django.urls import path

from . import views

app_name = "build_log"

urlpatterns = [
    path(
        "<uuid:project_id>/updates/",
        views.ProjectUpdateListCreateView.as_view(),
        name="update-list-create",
    ),
    path(
        "<uuid:project_id>/updates/<uuid:pk>/",
        views.ProjectUpdateDetailView.as_view(),
        name="update-detail",
    ),
    path(
        "<uuid:project_id>/updates/<uuid:pk>/photos/",
        views.UpdatePhotoUploadView.as_view(),
        name="update-photo-upload",
    ),
    path(
        "<uuid:project_id>/export-pdf/",
        views.ProjectExportView.as_view(),
        name="export-pdf",
    ),
]
