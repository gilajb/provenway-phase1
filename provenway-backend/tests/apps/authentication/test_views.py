import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.profiles.models import Profile


@pytest.fixture
def api_client():
    return APIClient()


def _make_user(email="joy@example.com", **kwargs):
    kwargs.setdefault("display_name", "Joy Test")
    kwargs.setdefault("is_email_verified", True)
    return User.objects.create_user(email=email, password="StrongPass1", **kwargs)


@pytest.mark.django_db
class TestRegister:
    def test_register_creates_user_and_profile(self, api_client):
        response = api_client.post(
            reverse("authentication:register"),
            {
                "email": "newuser@example.com",
                "password": "StrongPass1",
                "display_name": "New User",
            },
            format="json",
        )
        assert response.status_code == 201
        user = User.objects.get(email="newuser@example.com")
        assert Profile.objects.filter(user=user).exists()
        # avatar_url/disciplines now come from Profile via
        # CurrentUserSerializer's SerializerMethodFields — should be
        # empty defaults for a brand new user, not error out.
        assert response.data["user"]["avatar_url"] is None
        assert response.data["user"]["disciplines"] == []

    def test_register_does_not_accept_user_level_profile_fields(self, api_client):
        # bio/location/avatar_url no longer exist on User — RegisterSerializer
        # never accepted them, but confirm passing them doesn't error and
        # is simply ignored (not silently written anywhere on User).
        response = api_client.post(
            reverse("authentication:register"),
            {
                "email": "ignored@example.com",
                "password": "StrongPass1",
                "display_name": "Ignored Fields",
                "bio": "should be ignored",
            },
            format="json",
        )
        assert response.status_code == 201
        assert not hasattr(User.objects.get(email="ignored@example.com"), "bio")


@pytest.mark.django_db
class TestLoginAndMe:
    def test_login_reflects_profile_avatar_and_disciplines(self, api_client):
        user = _make_user(email="login@example.com")
        Profile.objects.filter(user=user).update(
            avatar_url="https://res.cloudinary.com/demo/avatar.jpg",
            disciplines=["civil_engineer", "structural_engineer"],
        )
        response = api_client.post(
            reverse("authentication:login"),
            {"email": "login@example.com", "password": "StrongPass1"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["user"]["avatar_url"] == "https://res.cloudinary.com/demo/avatar.jpg"
        assert set(response.data["user"]["disciplines"]) == {"civil_engineer", "structural_engineer"}

    def test_me_endpoint_reflects_profile_data(self, api_client):
        user = _make_user(email="me@example.com")
        Profile.objects.filter(user=user).update(avatar_url="https://example.com/a.png")
        # Re-fetch: the in-memory `user` cached its `.profile` reverse
        # relation when the post_save signal created it, and a queryset
        # `.update()` doesn't invalidate that cache. A real request never
        # hits this — MeView always loads request.user fresh from the DB.
        user = User.objects.get(pk=user.pk)
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("authentication:me"))
        assert response.status_code == 200
        assert response.data["avatar_url"] == "https://example.com/a.png"
        assert response.data["disciplines"] == []

    def test_unverified_email_can_still_login(self, api_client):
        # Email verification enforcement is disabled until Resend is wired
        # up — registering doesn't yet result in a deliverable email, so
        # gating login on it would lock out every real user.
        _make_user(email="unverified@example.com", is_email_verified=False)
        response = api_client.post(
            reverse("authentication:login"),
            {"email": "unverified@example.com", "password": "StrongPass1"},
            format="json",
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserModelNoLongerHasProfileFields:
    def test_dropped_fields_are_gone_from_user(self):
        user = _make_user(email="fields@example.com")
        for field in ("bio", "location_text", "location_lat", "location_lng", "avatar_url"):
            assert not hasattr(user, field), f"User.{field} should have been removed"

    def test_user_disciplines_related_name_is_gone(self):
        user = _make_user(email="nodisc@example.com")
        assert not hasattr(user, "disciplines"), (
            "UserDiscipline's related_name='disciplines' should no longer "
            "shadow anything on User — disciplines now live on Profile"
        )
