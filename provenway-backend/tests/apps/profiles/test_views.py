import io
from unittest.mock import patch

import pytest
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.profiles.models import Profile


@pytest.fixture
def api_client():
    return APIClient()


def _make_user(email="joy@example.com", **kwargs):
    kwargs.setdefault("display_name", "Joy Test")
    kwargs.setdefault("is_email_verified", True)
    user = User.objects.create_user(email=email, password="StrongPass1", **kwargs)
    return user


def _auth(api_client, user):
    api_client.force_authenticate(user=user)


@pytest.mark.django_db
class TestProfileAutoCreation:
    def test_profile_auto_created_on_user_creation(self):
        user = _make_user()
        assert Profile.objects.filter(user=user).exists()

    def test_profile_not_duplicated_on_user_resave(self):
        user = _make_user()
        assert Profile.objects.filter(user=user).count() == 1
        user.display_name = "Joy Updated"
        user.save()
        assert Profile.objects.filter(user=user).count() == 1


@pytest.mark.django_db
class TestMyProfileView:
    def test_get_requires_authentication(self, api_client):
        url = reverse("profiles:me")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_get_own_profile(self, api_client):
        user = _make_user()
        _auth(api_client, user)
        response = api_client.get(reverse("profiles:me"))
        assert response.status_code == 200
        assert response.data["user"]["id"] == str(user.id)
        assert response.data["is_own_profile"] is True

    def test_patch_updates_own_profile(self, api_client):
        user = _make_user()
        _auth(api_client, user)
        payload = {
            "bio": "Structural engineer with 8 years on-site.",
            "disciplines": ["structural_engineer", "civil_engineer"],
            "location_text": "Nairobi, Kenya",
            "years_experience": 8,
            "firm_name": "Cilneod Kenya",
        }
        response = api_client.patch(reverse("profiles:me"), payload, format="json")
        assert response.status_code == 200
        assert response.data["bio"] == payload["bio"]
        assert set(response.data["disciplines"]) == set(payload["disciplines"])
        assert response.data["firm_name"] == "Cilneod Kenya"

        profile = Profile.objects.get(user=user)
        assert profile.years_experience == 8

    def test_patch_rejects_invalid_discipline(self, api_client):
        user = _make_user()
        _auth(api_client, user)
        response = api_client.patch(
            reverse("profiles:me"), {"disciplines": ["astronaut"]}, format="json"
        )
        assert response.status_code == 400

    def test_patch_cannot_set_avatar_url_directly(self, api_client):
        user = _make_user()
        _auth(api_client, user)
        response = api_client.patch(
            reverse("profiles:me"),
            {"avatar_url": "https://evil.example.com/fake.png"},
            format="json",
        )
        assert response.status_code == 200
        profile = Profile.objects.get(user=user)
        assert profile.avatar_url != "https://evil.example.com/fake.png"

    def test_patch_bio_over_500_chars_rejected(self, api_client):
        user = _make_user()
        _auth(api_client, user)
        response = api_client.patch(
            reverse("profiles:me"), {"bio": "x" * 501}, format="json"
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestPublicProfileView:
    def test_anonymous_can_view_public_profile(self, api_client):
        user = _make_user(email="publicuser@example.com")
        Profile.objects.filter(user=user).update(bio="Public bio")
        response = api_client.get(reverse("profiles:public-profile", args=[user.id]))
        assert response.status_code == 200
        assert response.data["bio"] == "Public bio"
        assert response.data["is_own_profile"] is False

    def test_owner_viewing_own_profile_via_public_route_sees_is_own_profile_true(self, api_client):
        user = _make_user(email="ownviewer@example.com")
        _auth(api_client, user)
        response = api_client.get(reverse("profiles:public-profile", args=[user.id]))
        assert response.status_code == 200
        assert response.data["is_own_profile"] is True

    def test_nonexistent_user_returns_404(self, api_client):
        import uuid
        response = api_client.get(reverse("profiles:public-profile", args=[uuid.uuid4()]))
        assert response.status_code == 404

    def test_public_route_does_not_allow_patch(self, api_client):
        user = _make_user(email="another@example.com")
        other = _make_user(email="attacker@example.com")
        _auth(api_client, other)
        url = reverse("profiles:public-profile", args=[user.id])
        response = api_client.patch(url, {"bio": "hacked"}, format="json")
        assert response.status_code == 405


def _make_test_image_bytes(fmt="JPEG", size=(100, 100)):
    buf = io.BytesIO()
    Image.new("RGB", size, color=(255, 0, 0)).save(buf, format=fmt)
    buf.seek(0)
    return buf


@pytest.mark.django_db
class TestAvatarUploadView:
    def test_requires_authentication(self, api_client):
        response = api_client.post(reverse("profiles:me-avatar"), {}, format="multipart")
        assert response.status_code == 401

    @patch("apps.profiles.views.upload_avatar")
    def test_successful_avatar_upload(self, mock_upload, api_client):
        mock_upload.return_value = "https://res.cloudinary.com/demo/image/upload/avatar.jpg"
        user = _make_user(email="avataruser@example.com")
        _auth(api_client, user)

        image_bytes = _make_test_image_bytes()
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile("avatar.jpg", image_bytes.read(), content_type="image/jpeg")

        response = api_client.post(
            reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
        )
        assert response.status_code == 200
        assert response.data["avatar_url"] == "https://res.cloudinary.com/demo/image/upload/avatar.jpg"
        profile = Profile.objects.get(user=user)
        assert profile.avatar_url == "https://res.cloudinary.com/demo/image/upload/avatar.jpg"
        mock_upload.assert_called_once()

    def test_rejects_oversized_file(self, api_client):
        user = _make_user(email="bigfile@example.com")
        _auth(api_client, user)

        # Build an image whose encoded bytes exceed 5MB. A solid-color
        # image compresses far below that limit, so use random noise
        # (near-incompressible) instead of Image.new()'s flat fill.
        import os
        width, height = 1600, 1600
        noise = os.urandom(width * height * 3)
        buf = io.BytesIO()
        Image.frombytes("RGB", (width, height), noise).save(buf, format="PNG")
        buf.seek(0)
        content = buf.read()
        assert len(content) > 5 * 1024 * 1024

        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile("big.png", content, content_type="image/png")
        response = api_client.post(
            reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
        )
        assert response.status_code == 400

    def test_rejects_disallowed_content_type(self, api_client):
        user = _make_user(email="gifuser@example.com")
        _auth(api_client, user)

        image_bytes = _make_test_image_bytes(fmt="GIF")
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile("avatar.gif", image_bytes.read(), content_type="image/gif")

        response = api_client.post(
            reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
        )
        assert response.status_code == 400

    @patch("apps.profiles.views.upload_avatar")
    def test_cloudinary_failure_returns_502(self, mock_upload, api_client):
        from apps.profiles.service.cloudinary_service import CloudinaryUploadError
        mock_upload.side_effect = CloudinaryUploadError("boom")
        user = _make_user(email="failupload@example.com")
        _auth(api_client, user)

        image_bytes = _make_test_image_bytes()
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile("avatar.jpg", image_bytes.read(), content_type="image/jpeg")

        response = api_client.post(
            reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
        )
        assert response.status_code == 502


@pytest.mark.django_db
class TestAvatarUploadRateLimit:
    """Session 16 permission audit, item 5: avatar upload had no rate
    limiting at all — regression test for the fix in
    apps.profiles.views.AvatarUploadView (core.ratelimiting.enforce_rate_limit).
    """

    @patch("apps.profiles.views.upload_avatar")
    def test_exceeding_rate_limit_returns_429(self, mock_upload, api_client):
        from django.core.cache import cache
        from django.test import override_settings

        mock_upload.return_value = "https://res.cloudinary.com/demo/image/upload/avatar.jpg"
        user = _make_user(email="ratelimited-avatar@example.com")
        _auth(api_client, user)
        cache.clear()

        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for _ in range(11):  # limit is 10/h
                image_bytes = _make_test_image_bytes()
                from django.core.files.uploadedfile import SimpleUploadedFile
                upload = SimpleUploadedFile(
                    "avatar.jpg", image_bytes.read(), content_type="image/jpeg"
                )
                last_response = api_client.post(
                    reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
                )
            assert last_response.status_code == 429
        cache.clear()

    @patch("apps.profiles.views.upload_avatar")
    def test_rate_limit_is_keyed_per_user_not_shared(self, mock_upload, api_client):
        # A second user isn't blocked by the first user's uploads —
        # confirms the limit is keyed on `user`, not globally or by IP.
        from django.core.cache import cache
        from django.test import override_settings

        mock_upload.return_value = "https://res.cloudinary.com/demo/image/upload/avatar.jpg"
        user_a = _make_user(email="ratelimit-a@example.com")
        user_b = _make_user(email="ratelimit-b@example.com")
        cache.clear()

        with override_settings(RATELIMIT_ENABLE=True):
            _auth(api_client, user_a)
            for _ in range(10):
                image_bytes = _make_test_image_bytes()
                from django.core.files.uploadedfile import SimpleUploadedFile
                upload = SimpleUploadedFile(
                    "avatar.jpg", image_bytes.read(), content_type="image/jpeg"
                )
                api_client.post(
                    reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
                )

            _auth(api_client, user_b)
            image_bytes = _make_test_image_bytes()
            from django.core.files.uploadedfile import SimpleUploadedFile
            upload = SimpleUploadedFile(
                "avatar.jpg", image_bytes.read(), content_type="image/jpeg"
            )
            response = api_client.post(
                reverse("profiles:me-avatar"), {"avatar": upload}, format="multipart"
            )
            assert response.status_code == 200
        cache.clear()
