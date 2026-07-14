import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.authentication.models import Discipline


class Profile(models.Model):
    """Extended, editable professional profile — one-to-one with User.

    Single source of truth for bio / location / avatar / disciplines.
    apps.authentication.User used to carry its own duplicate copies of
    bio, location_text, location_lat, location_lng, and avatar_url, and a
    separate UserDiscipline join table duplicated `disciplines` below —
    both were retired in favour of this model (data migrated over in
    apps/authentication/migrations/0003 and 0005, columns dropped in 0004
    and 0006). Do not reintroduce these fields on User.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Postgres array of the same Discipline taxonomy used elsewhere, so
    # values stay consistent with apps.authentication.models.Discipline
    # without introducing a second choices list to keep in sync by hand.
    disciplines = ArrayField(
        base_field=models.CharField(max_length=30, choices=Discipline.choices),
        default=list,
        blank=True,
        help_text="Multi-select from the Discipline taxonomy.",
    )

    bio = models.TextField(max_length=500, null=True, blank=True)
    location_text = models.CharField(max_length=200, null=True, blank=True)
    location_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    location_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    years_experience = models.PositiveSmallIntegerField(null=True, blank=True)
    firm_name = models.CharField(max_length=200, null=True, blank=True)

    # Directory search (Session 12, GET /api/v1/users/). Denormalised
    # tsvector spanning this profile's own fields (bio, firm_name,
    # location_text) plus the linked User's display_name/headline, kept in
    # sync via apps.profiles.signals rather than recomputed per-request —
    # see apps/profiles/search.py for the weighting. Never set directly;
    # always written through search.update_search_vector().
    search_vector = SearchVectorField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profiles"
        indexes = [
            # Recreates the geographic-search composite index the schema
            # originally had on users.location_lat/location_lng
            # (Engineering Doc §3.2.1) before those columns moved to
            # Profile. It was dropped in authentication/migrations/0004
            # when the columns left User and was never re-added here —
            # radius search (this session) needs it, so it's added now.
            models.Index(
                fields=["location_lat", "location_lng"], name="profiles_location_idx"
            ),
            GinIndex(fields=["search_vector"], name="profiles_search_vector_gin"),
        ]

    def __str__(self):
        return f"Profile({self.user.email})"
