from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import User
from core.pagination import DefaultOffsetPagination
from core.ratelimiting import enforce_rate_limit

from .models import Follow
from .serializers import FollowerEntrySerializer, FollowingEntrySerializer


def _get_target_user(user_id):
    # is_active=True: a banned/deactivated user shouldn't be followable,
    # nor should their follower/following lists be browsable — matches
    # the same is_active gate apps.profiles.PublicProfileView uses.
    return get_object_or_404(User, pk=user_id, is_active=True)


class FollowToggleView(APIView):
    """POST/DELETE /users/{id}/follow/ — follow / unfollow a user.

    Both directions are deliberately idempotent (Engineering Doc doesn't
    say so explicitly, but a "follow" button toggling in a UI will retry
    or double-fire under real network conditions): following someone you
    already follow just returns the existing row rather than erroring,
    and unfollowing someone you don't follow is a no-op success rather
    than a 404.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        # Session 16 permission audit, item 5: follow/unfollow had no
        # rate limiting - spam-following (rapidly following/unfollowing
        # many accounts) generates unbounded DB writes today and would
        # generate unbounded notification spam once apps.notifications
        # exists. 30/min per user is generous for real usage (nobody
        # follows dozens of accounts a minute by hand) while bounding a
        # scripted flood.
        enforce_rate_limit(
            request, group="follow_toggle", rate="30/m", method=["POST", "DELETE"]
        )
        target = _get_target_user(user_id)

        follow = Follow(follower=request.user, following=target)
        try:
            follow.clean()
        except DjangoValidationError as exc:
            raise DRFValidationError({"detail": exc.messages})

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )
        return Response(
            {"is_following": True, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, user_id):
        enforce_rate_limit(
            request, group="follow_toggle", rate="30/m", method=["POST", "DELETE"]
        )
        target = _get_target_user(user_id)
        Follow.objects.filter(follower=request.user, following=target).delete()
        return Response({"is_following": False}, status=status.HTTP_200_OK)


class FollowersListView(generics.ListAPIView):
    """GET /users/{id}/followers/ — paginated list of who follows this user."""

    serializer_class = FollowerEntrySerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultOffsetPagination

    def get_queryset(self):
        target = _get_target_user(self.kwargs["user_id"])
        return (
            Follow.objects.filter(following=target)
            .select_related("follower")
            .order_by("-created_at")
        )


class FollowingListView(generics.ListAPIView):
    """GET /users/{id}/following/ — paginated list of who this user follows."""

    serializer_class = FollowingEntrySerializer
    permission_classes = [AllowAny]
    pagination_class = DefaultOffsetPagination

    def get_queryset(self):
        target = _get_target_user(self.kwargs["user_id"])
        return (
            Follow.objects.filter(follower=target)
            .select_related("following")
            .order_by("-created_at")
        )


class FollowStatusView(APIView):
    """GET /users/{id}/follow-status/ — does the requesting user follow this
    profile? (Powers follow-button UI state.)

    Also returns is_followed_by / is_mutual — not asked for explicitly, but
    cheap to compute alongside is_following and directly useful for a
    "Connection" badge, since Engineering Doc §1.4.1 defines mutual-follow
    as a connection.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        target = _get_target_user(user_id)
        is_following = Follow.objects.filter(
            follower=request.user, following=target
        ).exists()
        is_followed_by = Follow.objects.filter(
            follower=target, following=request.user
        ).exists()
        return Response(
            {
                "is_following": is_following,
                "is_followed_by": is_followed_by,
                "is_mutual": is_following and is_followed_by,
            }
        )
