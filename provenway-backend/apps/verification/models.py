import uuid

from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class DocumentType(models.TextChoices):
    LICENCE = "licence", "Professional Licence"
    DEGREE = "degree", "Degree Certificate"
    MEMBERSHIP = "membership", "Professional Body Membership"
    ID = "id", "Government ID"


class CredentialStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class VerificationCredential(TimestampedModel):
    """verification_credentials table (Engineering Doc §3.2.1 / §1.4.7).

    Approval sets User.is_verified=True via a post_save signal
    (apps/verification/signals.py) — deliberately one-way: a later
    rejection (e.g. a resubmission) never un-verifies an already-verified
    user. Revoking a verified badge, if ever needed, is a manual
    User.is_verified edit in admin, not an automated side effect of an
    unrelated rejected submission.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_credentials",
    )
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_url = models.URLField(max_length=500)
    status = models.CharField(
        max_length=20, choices=CredentialStatus.choices, default=CredentialStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_credentials",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Addition beyond the doc's literal field list — lets a rejected user
    # see why via GET /credentials/me/ rather than a bare status flip.
    rejection_reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "verification_credentials"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="cred_user_status_idx"),
        ]

    def __str__(self):
        return f"VerificationCredential({self.user_id}, {self.document_type}, {self.status})"
