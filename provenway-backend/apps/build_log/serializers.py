from django.utils import timezone
from rest_framework import serializers

from .models import EDIT_WINDOW, MAX_PHOTOS_PER_UPDATE, ProjectUpdate, UpdatePhoto

ALLOWED_PHOTO_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_PHOTO_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_PHOTO_SIZE_BYTES = 10 * 1024 * 1024  # 10MB per photo


class ProjectUpdateAuthorSummarySerializer(serializers.Serializer):
    """Minimal, read-only snapshot of the authoring User — same pattern as
    apps.projects.serializers.ProjectOwnerSummarySerializer.
    """

    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)


class UpdatePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdatePhoto
        fields = ["id", "url", "sequence_order", "created_at"]
        read_only_fields = fields


class ProjectUpdateSerializer(serializers.ModelSerializer):
    author = ProjectUpdateAuthorSummarySerializer(read_only=True)
    project = serializers.UUIDField(source="project_id", read_only=True)
    photos = UpdatePhotoSerializer(many=True, read_only=True)
    is_editable = serializers.SerializerMethodField()

    class Meta:
        model = ProjectUpdate
        fields = [
            "id",
            "project",
            "author",
            "title",
            "body",
            "entry_type",
            "entry_date",
            "geotag_lat",
            "geotag_lng",
            "exif_metadata",
            "photos",
            "is_editable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "author",
            "exif_metadata",
            "photos",
            "is_editable",
            "created_at",
            "updated_at",
        ]

    def get_is_editable(self, obj) -> bool:
        return timezone.now() < obj.created_at + EDIT_WINDOW


class UpdatePhotoUploadSerializer(serializers.Serializer):
    """Validates one or more photo files POSTed as `photos` (multipart,
    repeated field). Mirrors apps.profiles.serializers.AvatarUploadSerializer's
    validation (content-type + Pillow-decoded format, since the client
    content-type header is trivially spoofable) but for a list of files.
    """

    photos = serializers.ListField(
        child=serializers.ImageField(), allow_empty=False
    )

    def validate_photos(self, value):
        if len(value) > MAX_PHOTOS_PER_UPDATE:
            raise serializers.ValidationError(
                f"You can upload at most {MAX_PHOTOS_PER_UPDATE} photos in a single request."
            )
        for f in value:
            content_type = getattr(f, "content_type", "") or ""
            if content_type not in ALLOWED_PHOTO_CONTENT_TYPES:
                raise serializers.ValidationError(
                    "Photos must be JPEG, PNG, or WEBP images."
                )
            if f.size > MAX_PHOTO_SIZE_BYTES:
                raise serializers.ValidationError("Each photo must be 10MB or smaller.")

            pil_image = getattr(f, "image", None)
            if pil_image is not None and pil_image.format not in ALLOWED_PHOTO_PIL_FORMATS:
                raise serializers.ValidationError(
                    "Photos must be JPEG, PNG, or WEBP images."
                )
        return value
