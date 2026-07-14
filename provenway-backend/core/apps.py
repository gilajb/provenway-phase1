from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # provenway/celery_app.py defines the properly-configured Celery
        # app (eager mode in tests, the real broker URL in dev/prod), but
        # nothing was importing that module — provenway/__init__.py is
        # deliberately empty (Windows circular-import workaround), and no
        # other module referenced it either. Without this, every
        # @shared_task's .delay() call binds to Celery's *implicit*
        # default app (unconfigured, points at a local RabbitMQ broker
        # that doesn't exist here), so register/password-reset silently
        # 500 the moment they try to enqueue an email task.
        #
        # AppConfig.ready() fires only after Django's app registry is
        # fully populated, so importing celery_app here (rather than from
        # the package __init__) avoids the AppRegistryNotReady failure
        # that caused the original Windows issue, on every platform.
        #
        # Note: since __init__.py doesn't expose `app`/`celery`, start the
        # worker with `celery -A provenway.celery_app worker`, not the
        # shorter `-A provenway` (which relies on that convention).
        from provenway import celery_app  # noqa: F401
