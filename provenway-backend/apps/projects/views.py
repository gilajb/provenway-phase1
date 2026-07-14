from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.pagination import DefaultOffsetPagination
from core.permissions import IsOwnerOrReadOnly

from .models import Project
from .permissions import user_can_view_project, visible_projects_q
from .serializers import ProjectSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    """GET /api/v1/projects/ — list/search (optional auth).
    POST /api/v1/projects/ — create (auth required).
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = DefaultOffsetPagination

    def get_queryset(self):
        # Project.objects already excludes is_deleted rows (SoftDeleteModel's
        # default manager) — no explicit is_deleted filter needed here.
        qs = Project.objects.select_related("owner").prefetch_related("disciplines")
        user = self.request.user if self.request.user.is_authenticated else None

        # Public projects, anything the viewer owns, and connections-only
        # projects owned by a *mutual* connection of the viewer — see
        # apps.projects.permissions.visible_projects_q for the rule
        # (mirrors user_can_view_project; this is its queryset form).
        # This used to be built inline here; now shared with apps.feed,
        # which needs the identical rule applied to ProjectUpdate rows.
        qs = qs.filter(visible_projects_q(user))

        params = self.request.query_params
        discipline = params.get("discipline")
        if discipline:
            qs = qs.filter(disciplines__discipline=discipline)

        location = params.get("location")
        if location:
            qs = qs.filter(location_text__icontains=location)

        status_param = params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save()  # owner is set from request.user inside the serializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET /api/v1/projects/{id}/ — detail, visibility enforced (optional auth).
    PATCH /api/v1/projects/{id}/ — owner only.
    DELETE /api/v1/projects/{id}/ — owner only, soft-delete.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related("disciplines")

    def get_object(self):
        # Overridden (rather than relying on GenericAPIView.get_object)
        # because visibility enforcement has to happen before DRF's
        # object-level permission check, and has to result in a 404 — not
        # a 403 — for private/connections projects a viewer isn't
        # entitled to know exist at all.
        project = get_object_or_404(
            self.get_queryset(), pk=self.kwargs[self.lookup_url_kwarg]
        )
        user = self.request.user if self.request.user.is_authenticated else None

        if not user_can_view_project(project, user):
            raise Http404

        self.check_object_permissions(self.request, project)
        return project

    def perform_destroy(self, instance):
        instance.soft_delete()
