import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.networking.models import Follow


@pytest.fixture
def api_client():
    return APIClient()


def _make_user(email, **kwargs):
    kwargs.setdefault("display_name", "Test User")
    kwargs.setdefault("is_email_verified", True)
    return User.objects.create_user(email=email, password="StrongPass1", **kwargs)


def _auth(api_client, user):
    api_client.force_authenticate(user=user)


@pytest.mark.django_db
class TestFollowModel:
    def test_self_follow_rejected_by_clean(self):
        user = _make_user("selfcheck1@example.com")
        follow = Follow(follower=user, following=user)
        with pytest.raises(ValidationError):
            follow.clean()

    def test_self_follow_rejected_at_db_level(self):
        # Belt-and-braces: even bypassing clean(), the CheckConstraint
        # stops a self-follow row from ever being persisted.
        user = _make_user("selfcheck2@example.com")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Follow.objects.create(follower=user, following=user)

    def test_duplicate_follow_pair_rejected_at_db_level(self):
        a = _make_user("dupe-a@example.com")
        b = _make_user("dupe-b@example.com")
        Follow.objects.create(follower=a, following=b)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Follow.objects.create(follower=a, following=b)


@pytest.mark.django_db
class TestFollowToggleEndpoint:
    def test_follow_requires_authentication(self, api_client):
        _make_user("noauth-a@example.com")
        b = _make_user("noauth-b@example.com")
        response = api_client.post(reverse("networking:follow", args=[b.id]))
        assert response.status_code == 401

    def test_follow_creates_row(self, api_client):
        a = _make_user("follow-a@example.com")
        b = _make_user("follow-b@example.com")
        _auth(api_client, a)

        response = api_client.post(reverse("networking:follow", args=[b.id]))
        assert response.status_code == 201
        assert response.data["is_following"] is True
        assert response.data["created"] is True
        assert Follow.objects.filter(follower=a, following=b).exists()

    def test_follow_is_idempotent(self, api_client):
        a = _make_user("idem-a@example.com")
        b = _make_user("idem-b@example.com")
        _auth(api_client, a)

        first = api_client.post(reverse("networking:follow", args=[b.id]))
        second = api_client.post(reverse("networking:follow", args=[b.id]))

        assert first.status_code == 201
        assert second.status_code == 200
        assert second.data["created"] is False
        assert Follow.objects.filter(follower=a, following=b).count() == 1

    def test_cannot_follow_self(self, api_client):
        a = _make_user("selfapi@example.com")
        _auth(api_client, a)
        response = api_client.post(reverse("networking:follow", args=[a.id]))
        assert response.status_code == 400
        assert not Follow.objects.filter(follower=a, following=a).exists()

    def test_unfollow_requires_authentication(self, api_client):
        _make_user("nouauth-a@example.com")
        b = _make_user("nouauth-b@example.com")
        response = api_client.delete(reverse("networking:follow", args=[b.id]))
        assert response.status_code == 401

    def test_unfollow_removes_row(self, api_client):
        a = _make_user("unfollow-a@example.com")
        b = _make_user("unfollow-b@example.com")
        Follow.objects.create(follower=a, following=b)
        _auth(api_client, a)

        response = api_client.delete(reverse("networking:follow", args=[b.id]))
        assert response.status_code == 200
        assert response.data["is_following"] is False
        assert not Follow.objects.filter(follower=a, following=b).exists()

    def test_unfollow_is_idempotent_when_not_following(self, api_client):
        a = _make_user("neverfollowed-a@example.com")
        b = _make_user("neverfollowed-b@example.com")
        _auth(api_client, a)

        response = api_client.delete(reverse("networking:follow", args=[b.id]))
        assert response.status_code == 200
        assert response.data["is_following"] is False

    def test_follow_nonexistent_user_returns_404(self, api_client):
        import uuid

        a = _make_user("ghost-follower@example.com")
        _auth(api_client, a)
        response = api_client.post(reverse("networking:follow", args=[uuid.uuid4()]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestFollowToggleRateLimit:
    """Session 16 permission audit, item 5: follow/unfollow had no rate
    limiting at all — regression test for the fix in
    apps.networking.views.FollowToggleView.
    """

    def test_exceeding_rate_limit_returns_429(self, api_client):
        from django.core.cache import cache
        from django.test import override_settings

        follower = _make_user("spam-follower@example.com")
        targets = [_make_user(f"spam-target-{i}@example.com") for i in range(31)]
        _auth(api_client, follower)
        cache.clear()

        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for target in targets:  # limit is 30/m
                last_response = api_client.post(
                    reverse("networking:follow", args=[target.id])
                )
            assert last_response.status_code == 429
        cache.clear()

    def test_rate_limit_shared_across_follow_and_unfollow(self, api_client):
        # POST and DELETE share one budget — a script alternating
        # follow/unfollow to spam a target shouldn't get double the
        # allowance by splitting requests across the two methods.
        from django.core.cache import cache
        from django.test import override_settings

        follower = _make_user("spam-toggle@example.com")
        targets = [_make_user(f"toggle-target-{i}@example.com") for i in range(31)]
        _auth(api_client, follower)
        cache.clear()

        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for i, target in enumerate(targets):
                if i % 2 == 0:
                    last_response = api_client.post(
                        reverse("networking:follow", args=[target.id])
                    )
                else:
                    last_response = api_client.delete(
                        reverse("networking:follow", args=[target.id])
                    )
            assert last_response.status_code == 429
        cache.clear()


@pytest.mark.django_db
class TestFollowersFollowingLists:
    def test_followers_list_is_public(self, api_client):
        owner = _make_user("pub-owner@example.com")
        follower = _make_user("pub-follower@example.com")
        Follow.objects.create(follower=follower, following=owner)

        response = api_client.get(reverse("networking:followers", args=[owner.id]))
        assert response.status_code == 200
        ids = {row["user"]["id"] for row in response.data["results"]}
        assert str(follower.id) in ids

    def test_following_list_is_public(self, api_client):
        owner = _make_user("pub-owner2@example.com")
        followed = _make_user("pub-followed@example.com")
        Follow.objects.create(follower=owner, following=followed)

        response = api_client.get(reverse("networking:following", args=[owner.id]))
        assert response.status_code == 200
        ids = {row["user"]["id"] for row in response.data["results"]}
        assert str(followed.id) in ids

    def test_followers_list_paginated_and_excludes_unrelated_users(self, api_client):
        owner = _make_user("owner-list@example.com")
        follower = _make_user("follower-list@example.com")
        _make_user("unrelated-list@example.com")
        Follow.objects.create(follower=follower, following=owner)

        response = api_client.get(reverse("networking:followers", args=[owner.id]))
        assert response.status_code == 200
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestFollowStatusEndpoint:
    def test_requires_authentication(self, api_client):
        _make_user("status-noauth-a@example.com")
        b = _make_user("status-noauth-b@example.com")
        response = api_client.get(reverse("networking:follow-status", args=[b.id]))
        assert response.status_code == 401

    def test_reports_not_following(self, api_client):
        a = _make_user("status-a@example.com")
        b = _make_user("status-b@example.com")
        _auth(api_client, a)
        response = api_client.get(reverse("networking:follow-status", args=[b.id]))
        assert response.status_code == 200
        assert response.data["is_following"] is False
        assert response.data["is_mutual"] is False

    def test_reports_following(self, api_client):
        a = _make_user("status-c@example.com")
        b = _make_user("status-d@example.com")
        Follow.objects.create(follower=a, following=b)
        _auth(api_client, a)
        response = api_client.get(reverse("networking:follow-status", args=[b.id]))
        assert response.status_code == 200
        assert response.data["is_following"] is True

    def test_reports_mutual(self, api_client):
        a = _make_user("status-e@example.com")
        b = _make_user("status-f@example.com")
        Follow.objects.create(follower=a, following=b)
        Follow.objects.create(follower=b, following=a)
        _auth(api_client, a)
        response = api_client.get(reverse("networking:follow-status", args=[b.id]))
        assert response.status_code == 200
        assert response.data["is_following"] is True
        assert response.data["is_followed_by"] is True
        assert response.data["is_mutual"] is True
