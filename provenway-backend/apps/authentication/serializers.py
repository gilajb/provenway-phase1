from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password", "display_name", "phone"]

    def validate_password(self, value):
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )
        validate_password(value)
        return value

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )
        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password.", code="authorization"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been deactivated.", code="authorization"
            )
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )
        validate_password(value)
        return value


class CurrentUserSerializer(serializers.ModelSerializer):
    # avatar_url and disciplines now live on apps.profiles.Profile (the
    # single source of truth — see apps/profiles/models.py), not on User
    # directly. Sourced here via SerializerMethodField so
    # register/login/me responses keep returning them in one call rather
    # than requiring a second request to /profiles/me/.
    #
    # NOTE — response shape change: `disciplines` used to be a list of
    # UserDiscipline objects (`[{"discipline": "civil_engineer"}, ...]`).
    # Now that UserDiscipline has been retired in favour of
    # Profile.disciplines (a flat array field), this returns a plain list
    # of strings (`["civil_engineer", ...]`) instead. Frontend code
    # reading `user.disciplines[i].discipline` needs updating to read
    # `user.disciplines[i]` directly.
    avatar_url = serializers.SerializerMethodField()
    disciplines = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "phone", "display_name", "headline",
            "avatar_url", "is_verified", "is_email_verified", "subscription_tier",
            "disciplines", "created_at",
        ]
        read_only_fields = fields

    def get_avatar_url(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.avatar_url if profile else None

    def get_disciplines(self, obj):
        profile = getattr(obj, "profile", None)
        return list(profile.disciplines) if profile else []
