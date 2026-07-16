"""QR code generation for the PDF portfolio export — encodes a link back
to the project's live, verified build log (Engineering Doc §1.4.2).
"""
import io

import qrcode
from django.conf import settings


def generate_qr_png(project) -> io.BytesIO:
    """Returns a PNG image buffer encoding the project's public URL."""
    url = f"{settings.FRONTEND_BASE_URL}/projects/{project.id}/"
    img = qrcode.make(url, border=2)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
