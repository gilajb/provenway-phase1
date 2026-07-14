"""Server-side photo upload to Cloudinary for build log update photos.

Same deliberate deviation as apps.profiles.service.cloudinary_service: the
Engineering Doc's stated pattern (§4.2.2) is direct-to-Cloudinary upload
from the browser via a signed preset. This endpoint is backend-mediated
instead — the file is POSTed to Django, validated, then pushed to
Cloudinary — for the same reasons (simpler first pass, validation happens
server-side either way). Kept as its own module rather than importing
apps.profiles' version so apps/build_log doesn't reach into another app's
internals for something this small.
"""

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


def upload_update_photo(file_obj, update_id: str, sequence_order: int) -> dict:
    """Upload a validated image file to Cloudinary for a given update slot.

    `file_obj` is expected to already be validated (type + size) by
    UpdatePhotoUploadSerializer before this is called.

    Returns {"public_id": ..., "secure_url": ...}.
    """
    _ensure_configured()
    try:
        result = cloudinary.uploader.upload(
            file_obj,
            folder=f"provenway/updates/{update_id}",
            public_id=f"photo_{sequence_order}",
            overwrite=True,
            resource_type="image",
            transformation=[{"width": 1600, "crop": "limit", "quality": "auto:good"}],
        )
    except Exception as exc:  # cloudinary raises its own generic Error type
        raise CloudinaryUploadError(f"Photo upload failed: {exc}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise CloudinaryUploadError("Cloudinary did not return a URL for the uploaded photo.")
    return {"public_id": result.get("public_id"), "secure_url": secure_url}
