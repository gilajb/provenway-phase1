"""Server-side avatar upload to Cloudinary.

Note: the Engineering Doc's stated pattern for media (§4.2.2) is
direct-to-Cloudinary upload from the browser via a signed preset, with
Django only ever issuing signed params — never receiving file bytes. This
endpoint was explicitly requested as a backend-mediated upload instead
(the file is POSTed to Django, which validates it, then pushes it to
Cloudinary and returns the URL). That's a deliberate deviation for the
profile avatar path specifically; it's simpler for a first pass and the
validation happens server-side either way. Worth revisiting if avatar
uploads at scale make Django's request/response cycle a bottleneck.
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


def upload_avatar(file_obj, user_id: str) -> str:
    """Upload a validated image file to Cloudinary and return its secure URL.

    `file_obj` is expected to already be validated by
    AvatarUploadSerializer (type + size) before this is called — this
    function focuses purely on the upload, not re-validating input.
    """
    _ensure_configured()
    try:
        result = cloudinary.uploader.upload(
            file_obj,
            folder="provenway/avatars",
            public_id=f"user_{user_id}",
            overwrite=True,
            resource_type="image",
            transformation=[{"width": 512, "height": 512, "crop": "fill", "gravity": "face"}],
        )
    except Exception as exc:  # cloudinary raises its own generic Error type
        raise CloudinaryUploadError(f"Avatar upload failed: {exc}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise CloudinaryUploadError("Cloudinary did not return a URL for the uploaded avatar.")
    return secure_url
