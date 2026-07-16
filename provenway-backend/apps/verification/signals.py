from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CredentialStatus, VerificationCredential


@receiver(post_save, sender=VerificationCredential)
def cascade_approval_to_user(sender, instance, **kwargs):
    """Approving a credential sets User.is_verified — one-way, see the
    model docstring for why rejection never un-verifies.

    Saves `instance.user`, not `instance`, so this doesn't re-trigger
    itself. Admin actions call `.save()` per-object (not
    `queryset.update()`) specifically so this signal actually fires —
    see apps/verification/admin.py.
    """
    if instance.status != CredentialStatus.APPROVED:
        return
    if instance.user.is_verified:
        return
    instance.user.is_verified = True
    instance.user.save(update_fields=["is_verified"])
