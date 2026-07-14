import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)
RESEND_API_URL = "https://api.resend.com/emails"


class ResendError(Exception):
    pass


def _send(to, subject, html):
    api_key = settings.RESEND_API_KEY
    from_address = settings.RESEND_FROM_EMAIL

    if not api_key:
        logger.warning("RESEND_API_KEY is not configured — email not sent: %s", subject)
        return {"id": None, "skipped": True}

    response = requests.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"from": from_address, "to": [to], "subject": subject, "html": html},
        timeout=10,
    )

    if response.status_code >= 400:
        logger.error("Resend API error %s: %s", response.status_code, response.text)
        raise ResendError(f"Resend API returned {response.status_code}: {response.text}")

    return response.json()


def send_verification_email(to, display_name, verification_url):
    subject = "Verify your Provenway account"
    html = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color:#002e59;">Welcome to Provenway, {display_name}</h2>
      <p>Confirm your email address to activate your account. This link expires in 24 hours.</p>
      <p>
        <a href="{verification_url}"
           style="display:inline-block;background:#0c447c;color:#ffffff;
                  padding:12px 24px;border-radius:8px;text-decoration:none;">
          Verify my email
        </a>
      </p>
      <p style="color:#737781;font-size:13px;">
        If you didn't create a Provenway account, you can safely ignore this email.
      </p>
    </div>
    """
    return _send(to, subject, html)


def send_password_reset_email(to, display_name, reset_url):
    subject = "Reset your Provenway password"
    html = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 480px; margin: 0 auto;">
      <h2 style="color:#002e59;">Password reset requested</h2>
      <p>Hi {display_name}, click below to set a new password. This link expires in 1 hour.</p>
      <p>
        <a href="{reset_url}"
           style="display:inline-block;background:#0c447c;color:#ffffff;
                  padding:12px 24px;border-radius:8px;text-decoration:none;">
          Reset my password
        </a>
      </p>
      <p style="color:#737781;font-size:13px;">
        If you didn't request this, you can safely ignore this email.
      </p>
    </div>
    """
    return _send(to, subject, html)
