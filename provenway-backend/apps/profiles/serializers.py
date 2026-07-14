from rest_framework import serializers

from apps.authentication.models import Discipline

from .models import Profile

ALLOWED_AVATAR_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AVATAR_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class ProfileUserSummarySerializer(serializers.Serializer):
    """Minimal, read-only snapshot of the linked User.

    Kept as a plain Serializer (rather than importing
    apps.authentication.serializers.CurrentUserSerializer) so this app
    doesn't reach into authentication's serializer layer for a handful of
    display fields a profile card needs.
    """

    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    headline = serializers.CharField(read_only=True, allow_null=True)
    is_verified = serializers.BooleanField(read_only=True)
    subscription_tier = serializers.CharField(read_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    user = ProfileUserSummarySerializer(read_only=True)
    is_own_profile = serializers.SerializerMethodField()
    disciplines = serializers.ListField(
        child=serializers.ChoiceField(choices=Discipline.choices),
        required=False,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "disciplines",
            "bio",
            "location_text",
            "location_lat",
            "location_lng",
            "avatar_url",
            "years_experience",
            "firm_name",
            "is_own_profile",
            "created_at",
            "updated_at",
        ]
        # avatar_url is intentionally read-only here — it's only ever set
        # via AvatarUploadView after a real Cloudinary upload, never by a
        # client PATCHing an arbitrary URL string directly onto the field.
        read_only_fields = [
            "id",
            "user",
            "avatar_url",
            "created_at",
            "updated_at",
            "is_own_profile",
        ]

    def get_is_own_profile(self, obj) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not request or not user or not user.is_authenticated:
            return False
        return obj.user_id == user.id


class DirectorySearchResultSerializer(serializers.ModelSerializer):
    """One row of GET /api/v1/users/ (directory search) — just enough for
    a results-grid card. `id` is the User id (not the Profile id) since
    that's what every other profile-linking endpoint
    (GET /profiles/{user_id}/, follow/unfollow, etc.) keys off of.
    """

    id = serializers.UUIDField(source="user_id", read_only=True)
    display_name = serializers.CharField(source="user.display_name", read_only=True)
    headline = serializers.CharField(
        source="user.headline", read_only=True, allow_null=True
    )
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "display_name",
            "headline",
            "avatar_url",
            "location_text",
            "disciplines",
            "is_verified",
            "firm_name",
        ]


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

    def validate_avatar(self, value):
        content_type = getattr(value, "content_type", "") or ""
        if content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Avatar must be a JPEG, PNG, or WEBP image."
            )

        if value.size > MAX_AVATAR_SIZE_BYTES:
            raise serializers.ValidationError("Avatar must be 5MB or smaller.")

        # serializers.ImageField already opens the file with Pillow to
        # confirm it's a genuine, uncorrupted image (DRF stashes the
        # decoded PIL Image on `value.image`); cross-check the *actual*
        # decoded format too, not just the client-supplied content-type
        # header, since that header is trivially spoofable.
        pil_image = getattr(value, "image", None)
        if pil_image is not None and pil_image.format not in ALLOWED_AVATAR_PIL_FORMATS:
            raise serializers.ValidationError(
                "Avatar must be a JPEG, PNG, or WEBP image."
            )

        return value
