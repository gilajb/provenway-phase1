import logging

from celery import shared_task

from .service import email_service

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="email",
)
def send_verification_email_task(self, user_id, display_name, email, verification_url):
    try:
        email_service.send_verification_email(email, display_name, verification_url)
    except Exception as exc:
        logger.warning("Retrying send_verification_email_task for %s: %s", user_id, exc)
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="email",
)
def send_password_reset_email_task(self, user_id, display_name, email, reset_url):
    try:
        email_service.send_password_reset_email(email, display_name, reset_url)
    except Exception as exc:
        logger.warning("Retrying send_password_reset_email_task for %s: %s", user_id, exc)
        raise self.retry(exc=exc)
