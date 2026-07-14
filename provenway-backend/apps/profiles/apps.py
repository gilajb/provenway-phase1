from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.profiles"
    label = "profiles"
    verbose_name = "Profiles"

    def ready(self):
        # Registers the post_save receiver that auto-creates a blank
        # Profile for every new User. Imported inside ready() — same
        # reasoning as core/apps.py's celery_app import: this only fires
        # once Django's app registry is fully populated, which avoids
        # AppRegistryNotReady issues that a top-level import in models.py
        # or __init__.py could trigger.
        from . import signals  # noqa: F401
