from rest_framework import serializers

from apps.build_log.models import ProjectUpdate
from apps.build_log.serializers import UpdatePhotoSerializer


class FeedAuthorSerializer(serializers.Serializer):
    """Minimal author snapshot for a feed card.

    Same "plain Serializer, not the real model serializer" pattern as
    apps.build_log.serializers.ProjectUpdateAuthorSummarySerializer and
    apps.projects.serializers.ProjectOwnerSummarySerializer, but with
    avatar_url added — a feed card needs it since a feed spans many
    authors with no page-level avatar already shown (unlike a build-log
    timeline or project page, which already have one author/owner's
    avatar in the page header). Sourced from Profile the same way
    apps.authentication.serializers.CurrentUserSerializer.get_avatar_url
    does, since avatar_url lives on Profile, not User (Session 5).
    """

    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.avatar_url if profile else None


class FeedProjectSerializer(serializers.Serializer):
    """Minimal parent-project snapshot for a feed card — just enough to
    link back to the project (id) and label the card (title).
    """

    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)


class FeedItemSerializer(serializers.ModelSerializer):
    """One ProjectUpdate as it appears in the home feed (Engineering Doc
    §5.2 `GET /feed/`: "updates from followed users").

    Deliberately a separate serializer from
    apps.build_log.serializers.ProjectUpdateSerializer rather than a
    reuse of it: that serializer's `project` field is a bare UUID (fine
    on a project detail page, where the project is already the page's
    own context) and its author has no avatar_url (fine on a build-log
    timeline, where the page header already shows that one author's
    avatar). A feed card needs both author and project expanded inline,
    since a single feed page mixes many authors and many projects with
    nothing else on the page to supply that context.
    """

    author = FeedAuthorSerializer(read_only=True)
    project = FeedProjectSerializer(read_only=True)
    photos = UpdatePhotoSerializer(many=True, read_only=True)

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
            "photos",
            "created_at",
        ]
        read_only_fields = fields
