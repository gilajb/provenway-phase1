import uuid

from django.conf import settings
from django.db import models

from apps.authentication.models import Discipline
from core.models import SoftDeleteModel, TimestampedModel


class ProjectStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"


class ProjectVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    CONNECTIONS = "connections", "Connections"
    PRIVATE = "private", "Private"


class Project(TimestampedModel, SoftDeleteModel):
    """Build-log project — proof-of-work container for dated updates.

    Updates, photos, and co-signatures are deliberately out of scope for
    this pass (Engineering Doc §3.2.3 project_updates / update_photos /
    update_cosignatures tables) and land in the next session. This model
    only covers the `projects` table itself.

    Soft delete comes from core.models.SoftDeleteModel (is_deleted +
    deleted_at), which also gives us the same "excluded by default
    manager" behaviour used elsewhere in the codebase — Project.objects
    never returns soft-deleted rows; use Project.all_objects for that.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    location_text = models.CharField(max_length=300, null=True, blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.ACTIVE
    )
    visibility = models.CharField(
        max_length=20, choices=ProjectVisibility.choices, default=ProjectVisibility.PUBLIC
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "projects"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"], name="proj_owner_status_idx"),
            models.Index(fields=["visibility", "is_deleted"], name="proj_visibility_del_idx"),
        ]

    def __str__(self):
        return f"Project({self.title!r}, owner={self.owner_id})"


class ProjectDiscipline(models.Model):
    """project_disciplines join table — same Discipline taxonomy used by
    apps.authentication.Discipline / apps.profiles.Profile.disciplines.
    Reused directly rather than redefined, per the doc's instruction to
    keep a single taxonomy source.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="disciplines",
    )
    discipline = models.CharField(max_length=30, choices=Discipline.choices)

    class Meta:
        db_table = "project_disciplines"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "discipline"], name="unique_project_discipline"
            )
        ]

    def __str__(self):
        return f"{self.project_id}:{self.discipline}"
