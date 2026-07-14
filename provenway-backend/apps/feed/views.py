from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.build_log.models import ProjectUpdate
from apps.networking.models import Follow
from apps.projects.permissions import visible_projects_q

from .pagination import FeedCursorPagination
from .serializers import FeedItemSerializer


class FeedListView(generics.ListAPIView):
    """GET /api/v1/feed/ — Engineering Doc §5.2: "Home feed: updates from
    followed users, cursor-paginated."

    Scope for this session is this endpoint only. `/feed/discover/`
    (algorithmic discovery) and `/feed/trending/` (public, logged-out) are
    also listed in §5.2 but are deliberately out of scope here — see
    apps/feed/urls.py.

    Auth required (unlike most build-log/project read endpoints, which
    are optional-auth): a feed is inherently "your follow graph's
    activity", so there's nothing meaningful to return to an anonymous
    request.
    """

    serializer_class = FeedItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FeedCursorPagination

    def get_queryset(self):
        user = self.request.user

        # apps.networking.Follow is reused directly, not reimplemented —
        # per Engineering Doc §1.4.1, "who you follow" is exactly the
        # feed's source set.
        followed_ids = Follow.objects.filter(follower=user).values_list(
            "following_id", flat=True
        )

        return (
            ProjectUpdate.objects.filter(author_id__in=followed_ids)
            # Project's own default manager (which excludes soft-deleted
            # rows) isn't applied across a `project__` join, so this is
            # spelled out explicitly rather than assumed.
            .filter(project__is_deleted=False)
            # Same visibility rule already enforced on direct project/update
            # access (apps.projects.permissions.user_can_view_project),
            # applied here as its queryset-filter counterpart rather than
            # reimplemented — see visible_projects_q's docstring. In
            # practice this only ever *excludes* rows here (an update's
            # author is always its project's owner — see
            # apps.build_log.views.ProjectUpdateListCreateView.perform_create
            # — and Follow disallows self-follows, so the "owner==user"
            # branch of visible_projects_q never matches a followed
            # author's update); it's still applied via the shared helper,
            # not hand-trimmed to just the PUBLIC/CONNECTIONS cases, so
            # this stays correct automatically if either fact ever changes.
            .filter(visible_projects_q(user, prefix="project"))
            .select_related("author__profile", "project")
            .prefetch_related("photos")
            .order_by("-created_at", "-id")
        )
