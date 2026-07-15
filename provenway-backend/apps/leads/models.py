from django.db import models

from core.models import TimestampedModel, UUIDModel


class InterestSignup(UUIDModel, TimestampedModel):
    """Lead capture for product areas with no self-serve account flow yet
    (construction firms, educational institutions) — apps.organisations,
    apps.billing, apps.recruitment and apps.verification are all empty
    stubs, and Register only ever creates an individual account, so the
    marketing pages for those two audiences collect interest here instead
    of pointing at a signup flow that doesn't actually apply to them.

    Append-only: rows are never edited, only reviewed (see admin.py).
    """

    class InterestType(models.TextChoices):
        CONSTRUCTION_FIRM = "construction_firm", "Construction Firm"
        EDUCATIONAL_INSTITUTION = "educational_institution", "Educational Institution"

    name = models.CharField(max_length=200)
    email = models.EmailField()
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    interest_type = models.CharField(max_length=32, choices=InterestType.choices)
    message = models.TextField(blank=True, null=True)
    # Which marketing page the signup came from — free-text rather than an
    # enum since this is display/context metadata only, not something the
    # app branches logic on.
    source_page = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "interest_signups"
        indexes = [
            models.Index(fields=["interest_type", "-created_at"], name="lead_type_created_idx"),
        ]

    def __str__(self):
        return f"InterestSignup({self.email}, {self.interest_type})"
