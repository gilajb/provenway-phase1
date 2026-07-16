from rest_framework import serializers

from .models import CredentialStatus, DocumentType, VerificationCredential

ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10MB — larger than avatar's 5MB, scans can be big
PDF_MAGIC_BYTES = b"%PDF-"


class CredentialSubmitSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=DocumentType.choices)
    document = serializers.FileField()

    def validate_document(self, value):
        if value.size > MAX_DOCUMENT_SIZE_BYTES:
            raise serializers.ValidationError("Document must be 10MB or smaller.")

        content_type = getattr(value, "content_type", "") or ""

        if content_type == "application/pdf":
            # Magic-byte sniff rather than python-magic — that pulls in a
            # native libmagic dependency, the same Windows-fragility class
            # as WeasyPrint (see the PDF export feature's library choice).
            header = value.read(len(PDF_MAGIC_BYTES))
            value.seek(0)
            if header != PDF_MAGIC_BYTES:
                raise serializers.ValidationError(
                    "This file claims to be a PDF but isn't a valid one."
                )
            return value

        if content_type in ALLOWED_IMAGE_CONTENT_TYPES:
            # Re-decode with Pillow to cross-check the *actual* format,
            # not just the client-supplied (spoofable) content-type —
            # same pattern as apps.profiles.serializers.AvatarUploadSerializer.
            from PIL import Image, UnidentifiedImageError

            try:
                image = Image.open(value)
                image.verify()
                value.seek(0)
            except (UnidentifiedImageError, OSError) as exc:
                raise serializers.ValidationError(
                    "This file claims to be an image but isn't a valid one."
                ) from exc
            if image.format not in ALLOWED_IMAGE_PIL_FORMATS:
                raise serializers.ValidationError(
                    "Image must be a JPEG, PNG, or WEBP."
                )
            return value

        raise serializers.ValidationError(
            "Document must be a PDF, JPEG, PNG, or WEBP file."
        )


class CredentialSerializer(serializers.Serializer):
    """Explicit read whitelist — never __all__."""

    id = serializers.UUIDField(read_only=True)
    document_type = serializers.ChoiceField(choices=DocumentType.choices, read_only=True)
    document_url = serializers.URLField(read_only=True)
    status = serializers.ChoiceField(choices=CredentialStatus.choices, read_only=True)
    rejection_reason = serializers.CharField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True, allow_null=True)
