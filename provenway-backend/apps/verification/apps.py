from django.apps import AppConfig


class VerificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.verification"
    label = "verification"
    verbose_name = "Verification"

    def ready(self):
        # Wires the post_save cascade (approved credential -> User.is_verified).
        # Imported in ready(), not at module level, for the same reason
        # core/apps.py imports celery_app here — avoids AppRegistryNotReady.
        from . import signals  # noqa: F401
