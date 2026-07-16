"""Server-side credential document upload to Cloudinary.

Deliberately server-mediated (file POSTed to Django, validated, then
pushed to Cloudinary), not direct-to-Cloudinary from the browser like
build-log photos — credential documents are admin-reviewed and sensitive,
so they shouldn't ride a public unsigned upload preset. Matches the
apps.profiles avatar-upload precedent instead. Kept as its own module
rather than importing another app's service, same reasoning as
apps.build_log.service.cloudinary_service.
"""
import uuid

import cloudinary
import cloudinary.uploader
from django.conf import settings

_configured = False


class CloudinaryUploadError(Exception):
    """Raised when Cloudinary rejects or fails an upload."""


def _ensure_configured():
    global _configured
    if _configured:
        return
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _configured = True


def upload_credential_document(file_obj, user_id: str, document_type: str) -> dict:
    """Upload a validated credential document. `resource_type` is
    conditional: PDFs need "raw", images use "image" (so Cloudinary can
    still generate thumbnails/transformations for those later).

    Returns {"public_id": ..., "secure_url": ...}.
    """
    _ensure_configured()
    content_type = getattr(file_obj, "content_type", "") or ""
    resource_type = "raw" if content_type == "application/pdf" else "image"

    try:
        # public_id uses a fresh uuid, not the raw filename — real
        # filenames ("certificate (1).pdf") routinely contain characters
        # Cloudinary's public_id doesn't accept.
        result = cloudinary.uploader.upload(
            file_obj,
            folder=f"provenway/credentials/{user_id}",
            public_id=f"{document_type}_{uuid.uuid4().hex}",
            resource_type=resource_type,
        )
    except Exception as exc:  # cloudinary raises its own generic Error type
        raise CloudinaryUploadError(f"Document upload failed: {exc}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise CloudinaryUploadError("Cloudinary did not return a URL for the uploaded document.")
    return {"public_id": result.get("public_id"), "secure_url": secure_url}
