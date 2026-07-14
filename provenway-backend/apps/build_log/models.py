import uuid
from datetime import timedelta

import bleach
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.projects.models import Project
from core.models import SoftDeleteModel, TimestampedModel

# Engineering Doc §3.2.3: "up to 10 photos per entry" — sequence_order is
# 0-9, i.e. MAX_PHOTOS_PER_UPDATE slots.
MAX_PHOTOS_PER_UPDATE = 10

# Engineering Doc §5.2: PATCH .../updates/{uid}/ is "owner only, within 24h
# of creation". `created_at` (server-set) is the anchor — never entry_date,
# which is client-editable and represents the work date, not the edit
# window's start.
EDIT_WINDOW = timedelta(hours=24)

# Engineering Doc §6.1 (A03: Injection): "Bleach/DOMPurify sanitisation on
# both client (React) and server; whitelist-only HTML tags." This is the
# server half of that — bleach was added to requirements/base.txt
# specifically for this (it wasn't already a dependency; flagging the
# addition since nothing else in the codebase pulled it in).
ALLOWED_BODY_TAGS = [
    "p", "br", "strong", "em", "u", "s", "ul", "ol", "li",
    "h3", "h4", "blockquote", "a", "code", "pre",
]
ALLOWED_BODY_ATTRS = {"a": ["href", "title", "rel"]}


def sanitize_rich_text(raw: str) -> str:
    if not raw:
        return raw
    return bleach.clean(
        raw, tags=ALLOWED_BODY_TAGS, attributes=ALLOWED_BODY_ATTRS, strip=True
    )


class EntryType(models.TextChoices):
    MILESTONE = "milestone", "Milestone"
    DAILY_LOG = "daily_log", "Daily Log"
    ISSUE = "issue", "Issue / Resolution"
    INSPECTION = "inspection", "Inspection Passed"
    PHASE_COMPLETE = "phase_complete", "Phase Complete"


class ProjectUpdate(TimestampedModel, SoftDeleteModel):
    """project_updates table (Engineering Doc §3.2.3).

    Visibility is deliberately NOT re-implemented here: an update is only
    ever reachable through its parent Project, and every view in this app
    gates access through apps.projects.permissions.user_can_view_project
    against that parent before ever touching a ProjectUpdate queryset.

    `created_at` (TimestampedModel, auto_now_add) is the server-set
    timestamp used for the 24-hour edit window. `entry_date` below is a
    separate, client-set field for the actual work date — the doc is
    explicit these must never be conflated.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_updates",
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, default="")
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    entry_date = models.DateField()
    geotag_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geotag_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # Raw EXIF pulled from uploaded photos, keyed by photo id — populated
    # by the photo upload endpoint, never client-writable directly.
    exif_metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "project_updates"
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["project", "entry_date"], name="update_proj_entrydate_idx"),
            models.Index(fields=["author", "created_at"], name="update_author_created_idx"),
        ]

    def save(self, *args, **kwargs):
        self.body = sanitize_rich_text(self.body)
        super().save(*args, **kwargs)

    @property
    def edit_window_closed(self) -> bool:
        return timezone.now() >= self.created_at + EDIT_WINDOW

    def __str__(self):
        return f"ProjectUpdate({self.title!r}, project={self.project_id})"


class UpdatePhoto(models.Model):
    """update_photos table (Engineering Doc §3.2.3)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    update = models.ForeignKey(ProjectUpdate, on_delete=models.CASCADE, related_name="photos")
    cloudinary_public_id = models.CharField(max_length=300)
    url = models.URLField(max_length=500)
    sequence_order = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_PHOTOS_PER_UPDATE - 1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "update_photos"
        ordering = ["sequence_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["update", "sequence_order"], name="unique_update_sequence_order"
            )
        ]

    def __str__(self):
        return f"UpdatePhoto(update={self.update_id}, seq={self.sequence_order})"
