from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import Discipline
from core.pagination import DefaultOffsetPagination
from core.ratelimiting import enforce_rate_limit

from .models import Profile
from .permissions import IsProfileOwner
from .search import annotate_distance_km, bounding_box
from .serializers import (
    AvatarUploadSerializer,
    DirectorySearchResultSerializer,
    ProfileSerializer,
)
from .service.cloudinary_service import CloudinaryUploadError, upload_avatar


class MyProfileView(APIView):
    """GET/PATCH the current authenticated user's own profile.

    Routing by /me/ already guarantees this only ever touches
    request.user's own row, but check_object_permissions() is still called
    explicitly (IsProfileOwner) as a deliberate defense-in-depth match to
    the object-level permission audit pattern used across the rest of the
    API — never rely on the URL alone to guarantee ownership.
    """

    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get(self, request):
        profile, _ = Profile.objects.select_related("user").get_or_create(
            user=request.user
        )
        self.check_object_permissions(request, profile)
        return Response(ProfileSerializer(profile, context={"request": request}).data)

    def patch(self, request):
        # get_or_create as a defensive fallback — the post_save signal on
        # User already guarantees a Profile exists for every registered
        # user, but this keeps the endpoint correct even for
        # pre-existing/fixture users created before this app was wired up.
        profile, _ = Profile.objects.select_related("user").get_or_create(
            user=request.user
        )
        self.check_object_permissions(request, profile)
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicProfileView(APIView):
    """GET another user's public profile by user_id."""

    permission_classes = [AllowAny]

    def get(self, request, user_id):
        profile = get_object_or_404(
            Profile.objects.select_related("user"),
            user_id=user_id,
            user__is_active=True,
        )
        return Response(ProfileSerializer(profile, context={"request": request}).data)


class AvatarUploadView(APIView):
    """POST a new avatar image; uploads to Cloudinary and stores the URL."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Session 16 permission audit, item 5: avatar upload had no rate
        # limiting despite hitting Cloudinary on every call — a single
        # account could flood the upload endpoint (cost + abuse vector).
        # 10/hour per user is generous for legitimate use (nobody changes
        # their avatar more than a handful of times an hour) while
        # bounding the damage of a flood.
        enforce_rate_limit(request, group="avatar_upload", rate="10/h")
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avatar_file = serializer.validated_data["avatar"]

        profile, _ = Profile.objects.get_or_create(user=request.user)

        try:
            avatar_url = upload_avatar(avatar_file, user_id=str(request.user.id))
        except CloudinaryUploadError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        profile.avatar_url = avatar_url
        profile.save(update_fields=["avatar_url", "updated_at"])

        return Response(
            ProfileSerializer(profile, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


def _parse_bool(raw: str, param_name: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in ("true", "1", "yes"):
        return True
    if lowered in ("false", "0", "no"):
        return False
    raise ValidationError({param_name: [f"'{raw}' is not a valid boolean."]})


def _parse_float(raw: str, param_name: str) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        raise ValidationError({param_name: [f"'{raw}' is not a valid number."]})


def _parse_disciplines(params) -> list:
    """Accepts either repeated `?discipline=a&discipline=b` or a single
    comma-separated `?discipline=a,b` — frontends tend to do one or the
    other depending on how their filter UI serialises multi-select state,
    so both are supported rather than picking one and surprising the
    other.
    """
    raw_values = []
    for value in params.getlist("discipline"):
        raw_values.extend(part.strip() for part in value.split(",") if part.strip())

    valid = {choice for choice, _ in Discipline.choices}
    invalid = [v for v in raw_values if v not in valid]
    if invalid:
        raise ValidationError(
            {"discipline": [f"Unknown discipline(s): {', '.join(invalid)}."]}
        )
    return raw_values


class DirectorySearchView(generics.ListAPIView):
    """GET /api/v1/users/ — searchable professional directory
    (Engineering Doc §5.2, FR under §1.4.1). Optional auth; results are
    the same for logged-out and logged-in callers (there's no
    connections-only tier for directory visibility, unlike Projects).

    Query params:
      q            — full-text search across display_name, headline,
                      bio, firm_name (PostgreSQL FTS against
                      Profile.search_vector, GIN-indexed — see
                      apps/profiles/search.py)
      discipline   — one or more Discipline values (repeated param or
                      comma-separated)
      location     — free-text match against location_text
      lat/lng/radius_km — geographic radius search instead of `location`;
                      all three must be present together
      verified     — "true"/"false", filters on is_verified

    Scope note: this only searches profiles/users. Cross-model search
    (jobs, tenders) belongs to apps.search once that app is scaffolded —
    deliberately not built here.
    """

    serializer_class = DirectorySearchResultSerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultOffsetPagination

    def get_queryset(self):
        params = self.request.query_params

        qs = Profile.objects.select_related("user").filter(user__is_active=True)

        disciplines = _parse_disciplines(params)
        if disciplines:
            qs = qs.filter(disciplines__overlap=disciplines)

        verified_raw = params.get("verified")
        if verified_raw is not None:
            qs = qs.filter(user__is_verified=_parse_bool(verified_raw, "verified"))

        lat_raw, lng_raw, radius_raw = (
            params.get("lat"),
            params.get("lng"),
            params.get("radius_km"),
        )
        geo_params_given = [p for p in (lat_raw, lng_raw, radius_raw) if p is not None]
        if geo_params_given and len(geo_params_given) != 3:
            raise ValidationError(
                {
                    "detail": "lat, lng, and radius_km must all be provided together for radius search."
                }
            )

        use_geo = len(geo_params_given) == 3
        if use_geo:
            lat = _parse_float(lat_raw, "lat")
            lng = _parse_float(lng_raw, "lng")
            radius_km = _parse_float(radius_raw, "radius_km")
            if radius_km <= 0:
                raise ValidationError({"radius_km": ["Must be a positive number."]})

            box = bounding_box(lat, lng, radius_km)
            qs = qs.filter(
                location_lat__isnull=False,
                location_lng__isnull=False,
                location_lat__gte=box["lat_min"],
                location_lat__lte=box["lat_max"],
                location_lng__gte=box["lng_min"],
                location_lng__lte=box["lng_max"],
            )
            qs = annotate_distance_km(qs, lat, lng).filter(distance_km__lte=radius_km)
        else:
            location = params.get("location")
            if location:
                qs = qs.filter(location_text__icontains=location)

        q = params.get("q")
        if q:
            query = SearchQuery(q, config="english", search_type="websearch")
            qs = qs.filter(search_vector=query).annotate(
                rank=SearchRank(F("search_vector"), query)
            )

        # Ordering priority: text-relevance rank, then geo distance, then
        # a stable, sensible default.
        if q:
            qs = qs.order_by("-rank", "-created_at")
        elif use_geo:
            qs = qs.order_by("distance_km")
        else:
            qs = qs.order_by("-created_at")

        return qs
