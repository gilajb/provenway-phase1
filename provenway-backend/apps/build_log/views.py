from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.projects.permissions import user_can_view_project
from core.pagination import DefaultOffsetPagination
from core.ratelimiting import enforce_rate_limit

from .models import EDIT_WINDOW, MAX_PHOTOS_PER_UPDATE, ProjectUpdate, UpdatePhoto
from .permissions import IsProjectOwnerOrReadOnly
from .serializers import (
    ProjectUpdateSerializer,
    UpdatePhotoSerializer,
    UpdatePhotoUploadSerializer,
)
from .service.cloudinary_service import CloudinaryUploadError, upload_update_photo
from .service.exif_service import extract_exif


def _get_visible_project(request, project_id):
    """Shared lookup: 404s (never leaks via 403) for a project the
    requesting user isn't entitled to see at all, per the same rule
    apps.projects.views enforces for the Project endpoints themselves.
    """
    project = get_object_or_404(
        Project.objects.select_related("owner"), pk=project_id
    )
    user = request.user if request.user.is_authenticated else None
    if not user_can_view_project(project, user):
        raise Http404
    return project


class ProjectUpdateListCreateView(generics.ListCreateAPIView):
    """GET /api/v1/projects/{project_id}/updates/ — list updates for a
    project; visibility inherited from the parent Project (optional auth).
    POST /api/v1/projects/{project_id}/updates/ — create; project owner only.
    """

    serializer_class = ProjectUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = DefaultOffsetPagination

    def get_queryset(self):
        project = _get_visible_project(self.request, self.kwargs["project_id"])
        return (
            ProjectUpdate.objects.filter(project=project)
            .select_related("author", "project__owner")
            .prefetch_related("photos")
        )

    def perform_create(self, serializer):
        # Visibility check first (404 for anything the requester can't see
        # at all — public-but-not-owner never trips this), then ownership
        # (403 for a public project the requester can see but doesn't own).
        project = _get_visible_project(self.request, self.kwargs["project_id"])
        if project.owner_id != self.request.user.id:
            raise PermissionDenied("Only the project owner can add update entries.")
        serializer.save(project=project, author=self.request.user)


class ProjectUpdateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET /api/v1/projects/{project_id}/updates/{uid}/ — detail.
    PATCH — project owner only, AND only within 24h of creation.
    DELETE — project owner only, soft-delete.
    """

    serializer_class = ProjectUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsProjectOwnerOrReadOnly]
    lookup_url_kwarg = "pk"

    def get_object(self):
        # Overridden for the same reason apps.projects.views.ProjectDetailView
        # overrides it: visibility has to be enforced (and result in 404,
        # not 403) before DRF's object-level permission check ever runs.
        project = _get_visible_project(self.request, self.kwargs["project_id"])
        update = get_object_or_404(
            ProjectUpdate.objects.filter(project=project)
            .select_related("author", "project__owner")
            .prefetch_related("photos"),
            pk=self.kwargs[self.lookup_url_kwarg],
        )
        self.check_object_permissions(self.request, update)
        return update

    def perform_update(self, serializer):
        instance = serializer.instance
        if timezone.now() >= instance.created_at + EDIT_WINDOW:
            raise PermissionDenied(
                "This update can no longer be edited — the 24-hour edit "
                "window has closed."
            )
        serializer.save()

    def perform_destroy(self, instance):
        instance.soft_delete()


class UpdatePhotoUploadView(APIView):
    """POST /api/v1/projects/{project_id}/updates/{uid}/photos/ — project
    owner only. Uploads to Cloudinary, enforces the 10-photo cap and
    sequence_order 0-9, and extracts EXIF into the update's exif_metadata.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, pk):
        # Session 16 permission audit, item 5: photo upload had no rate
        # limiting despite doing a Cloudinary upload plus EXIF extraction
        # per file (up to 10 photos in one call). The 10-photo-per-update
        # cap bounds a single update, but nothing stopped repeated calls
        # across many updates/projects from flooding uploads. 30/hour per
        # user comfortably covers real build-log usage while bounding
        # flood damage.
        enforce_rate_limit(request, group="update_photo_upload", rate="30/h")
        project = _get_visible_project(request, project_id)
        update = get_object_or_404(
            ProjectUpdate.objects.filter(project=project).select_related("project__owner"),
            pk=pk,
        )

        if update.project.owner_id != request.user.id:
            raise PermissionDenied("Only the project owner can upload photos to this update.")

        serializer = UpdatePhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = serializer.validated_data["photos"]

        existing_count = update.photos.count()
        if existing_count + len(files) > MAX_PHOTOS_PER_UPDATE:
            raise ValidationError(
                f"This update already has {existing_count} photo(s); uploading "
                f"{len(files)} more would exceed the {MAX_PHOTOS_PER_UPDATE}-photo limit."
            )

        created_photos = []
        exif_by_photo_id = {}
        next_seq = existing_count

        for f in files:
            exif_data = extract_exif(f)

            try:
                upload_result = upload_update_photo(
                    f, update_id=str(update.id), sequence_order=next_seq
                )
            except CloudinaryUploadError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

            photo = UpdatePhoto.objects.create(
                update=update,
                cloudinary_public_id=upload_result["public_id"],
                url=upload_result["secure_url"],
                sequence_order=next_seq,
            )
            created_photos.append(photo)
            if exif_data:
                exif_by_photo_id[str(photo.id)] = exif_data
            next_seq += 1

        if exif_by_photo_id:
            update.exif_metadata = {**(update.exif_metadata or {}), **exif_by_photo_id}
            update.save(update_fields=["exif_metadata", "updated_at"])

        return Response(
            UpdatePhotoSerializer(created_photos, many=True).data,
            status=status.HTTP_201_CREATED,
        )
