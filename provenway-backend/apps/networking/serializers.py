from rest_framework import serializers


class FollowUserSummarySerializer(serializers.Serializer):
    """Minimal, read-only snapshot of a User for followers/following lists.

    Same plain-Serializer pattern as apps.projects.ProjectOwnerSummarySerializer
    and apps.profiles.ProfileUserSummarySerializer — kept local instead of
    importing authentication's own serializer layer for a handful of
    display fields a follower/following row needs.
    """

    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    headline = serializers.CharField(read_only=True, allow_null=True)
    is_verified = serializers.BooleanField(read_only=True)


class FollowerEntrySerializer(serializers.Serializer):
    """One row of a GET /users/{id}/followers/ response — the follower's
    user summary plus when the Follow was created."""

    user = FollowUserSummarySerializer(source="follower", read_only=True)
    followed_at = serializers.DateTimeField(source="created_at", read_only=True)


class FollowingEntrySerializer(serializers.Serializer):
    """One row of a GET /users/{id}/following/ response — the followed
    user's summary plus when the Follow was created."""

    user = FollowUserSummarySerializer(source="following", read_only=True)
    followed_at = serializers.DateTimeField(source="created_at", read_only=True)
