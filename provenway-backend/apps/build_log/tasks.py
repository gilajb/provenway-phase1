import logging

from celery import shared_task

from apps.projects.models import Project

from .service.cloudinary_service import CloudinaryUploadError, upload_export_pdf
from .service.pdf_export_service import build_portfolio_pdf

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    queue="exports",
)
def generate_project_pdf_task(self, project_id):
    """Generates and uploads a project's PDF portfolio. Polled via
    ProjectExportStatusView (apps.build_log.views) against this task's
    AsyncResult — on terminal failure (retries exhausted), this must end
    in Celery's FAILURE state so the status view can report it cleanly,
    which `self.retry(exc=exc)` already does once max_retries is hit.
    """
    try:
        project = Project.objects.get(pk=project_id)
        pdf_bytes = build_portfolio_pdf(project)
        upload_result = upload_export_pdf(pdf_bytes, project_id)
        return {"pdf_url": upload_result["secure_url"]}
    except Project.DoesNotExist:
        # Not transient — retrying won't make a deleted/missing project
        # reappear, so fail immediately rather than burning retries.
        logger.error("generate_project_pdf_task: project %s not found", project_id)
        raise
    except CloudinaryUploadError as exc:
        logger.warning("Retrying generate_project_pdf_task for project %s: %s", project_id, exc)
        raise self.retry(exc=exc)
