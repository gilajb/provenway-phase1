from django.contrib import admin
from django.utils import timezone

from .models import CredentialStatus, VerificationCredential


@admin.register(VerificationCredential)
class VerificationCredentialAdmin(admin.ModelAdmin):
    list_display = ["user", "document_type", "status", "reviewed_by", "created_at"]
    list_filter = ["status", "document_type"]
    search_fields = ["user__email", "user__display_name"]
    # status/rejection_reason are deliberately left editable (not in
    # readonly_fields) — the bulk actions below cover the common case,
    # but this lets an admin open one credential's detail page, set
    # status to rejected, and type a reason directly. Either path calls
    # .save() (the admin's normal change-form save does too), so both
    # correctly trigger the post_save cascade signal.
    readonly_fields = [
        "id", "user", "document_type", "document_url",
        "reviewed_by", "reviewed_at", "created_at", "updated_at",
    ]
    actions = ["approve_credentials", "reject_credentials"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Approve selected credentials")
    def approve_credentials(self, request, queryset):
        # Plain loop, not queryset.update() — .update() bypasses .save()
        # and would silently skip the post_save signal that cascades
        # approval to User.is_verified (apps/verification/signals.py).
        for credential in queryset:
            credential.status = CredentialStatus.APPROVED
            credential.reviewed_by = request.user
            credential.reviewed_at = timezone.now()
            credential.rejection_reason = None
            credential.save()

    @admin.action(description="Reject selected credentials")
    def reject_credentials(self, request, queryset):
        for credential in queryset:
            credential.status = CredentialStatus.REJECTED
            credential.reviewed_by = request.user
            credential.reviewed_at = timezone.now()
            credential.save()
