from rest_framework import serializers

from .models import InterestSignup


class InterestSignupSerializer(serializers.Serializer):
    """Plain Serializer (not ModelSerializer) with an explicit field
    whitelist, per CLAUDE.md's "never __all__" convention.

    `website` is a honeypot: real visitors never see or fill this field
    (hidden via CSS on the form), so a non-empty value marks the
    submission as spam. It's write-only and deliberately never persisted.
    """

    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    organization_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    interest_type = serializers.ChoiceField(choices=InterestSignup.InterestType.choices)
    message = serializers.CharField(required=False, allow_blank=True)
    source_page = serializers.CharField(max_length=100, required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def create(self, validated_data):
        validated_data.pop("website", None)
        return InterestSignup.objects.create(**validated_data)
