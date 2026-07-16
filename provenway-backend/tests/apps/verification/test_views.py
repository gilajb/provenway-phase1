import io
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.verification.admin import VerificationCredentialAdmin
from apps.verification.models import CredentialStatus, VerificationCredential
from django.contrib import admin as django_admin


@pytest.fixture
def api_client():
    return APIClient()


def _make_user(email, **kwargs):
    kwargs.setdefault("display_name", "Test User")
    kwargs.setdefault("is_email_verified", True)
    return User.objects.create_user(email=email, password="StrongPass1", **kwargs)


def _auth(api_client, user):
    api_client.force_authenticate(user=user)


def _tiny_jpeg_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _uploaded_image(name="license.jpg"):
    return SimpleUploadedFile(name, _tiny_jpeg_bytes(), content_type="image/jpeg")


def _uploaded_pdf(name="license.pdf", valid=True):
    content = b"%PDF-1.4 fake pdf content" if valid else b"NOT-A-REAL-PDF"
    return SimpleUploadedFile(name, content, content_type="application/pdf")


def _submit_url():
    return reverse("verification:submit")


def _me_url():
    return reverse("verification:me")


@pytest.mark.django_db
class TestCredentialSubmitView:
    def test_requires_authentication(self, api_client):
        response = api_client.post(_submit_url(), {"document_type": "licence", "document": _uploaded_image()})
        assert response.status_code == 401

    @patch("apps.verification.views.upload_credential_document")
    def test_valid_image_submission_creates_pending_credential(self, mock_upload, api_client):
        user = _make_user("submit-image@example.com")
        _auth(api_client, user)
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/x/license.jpg"}

        response = api_client.post(
            _submit_url(),
            {"document_type": "licence", "document": _uploaded_image()},
            format="multipart",
        )

        assert response.status_code == 201
        assert response.data["status"] == "pending"
        credential = VerificationCredential.objects.get(user=user)
        assert credential.document_url == "https://res.cloudinary.com/x/license.jpg"

    @patch("apps.verification.views.upload_credential_document")
    def test_valid_pdf_submission_creates_pending_credential(self, mock_upload, api_client):
        user = _make_user("submit-pdf@example.com")
        _auth(api_client, user)
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/x/degree.pdf"}

        response = api_client.post(
            _submit_url(),
            {"document_type": "degree", "document": _uploaded_pdf()},
            format="multipart",
        )

        assert response.status_code == 201
        assert VerificationCredential.objects.filter(user=user, document_type="degree").exists()

    def test_pdf_with_bad_magic_bytes_rejected(self, api_client):
        user = _make_user("submit-badpdf@example.com")
        _auth(api_client, user)

        response = api_client.post(
            _submit_url(),
            {"document_type": "degree", "document": _uploaded_pdf(valid=False)},
            format="multipart",
        )
        assert response.status_code == 400

    def test_invalid_image_bytes_rejected(self, api_client):
        user = _make_user("submit-badimg@example.com")
        _auth(api_client, user)
        garbage = SimpleUploadedFile("license.jpg", b"not-an-image", content_type="image/jpeg")

        response = api_client.post(
            _submit_url(), {"document_type": "licence", "document": garbage}, format="multipart"
        )
        assert response.status_code == 400

    @patch("apps.verification.views.upload_credential_document")
    def test_rate_limit_returns_429_after_ten_per_day(self, mock_upload, api_client):
        from django.core.cache import cache
        from django.test import override_settings

        user = _make_user("submit-ratelimit@example.com")
        _auth(api_client, user)
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/x/doc.jpg"}
        cache.clear()

        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for _ in range(11):  # limit is 10/d
                last_response = api_client.post(
                    _submit_url(),
                    {"document_type": "licence", "document": _uploaded_image()},
                    format="multipart",
                )
            assert last_response.status_code == 429
        cache.clear()


@pytest.mark.django_db
class TestCredentialMeView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(_me_url())
        assert response.status_code == 401

    def test_returns_only_own_credentials_newest_first(self, api_client):
        from datetime import timedelta

        from django.utils import timezone

        user = _make_user("me-view@example.com")
        other = _make_user("me-view-other@example.com")
        _auth(api_client, user)

        VerificationCredential.objects.create(
            user=other, document_type="licence", document_url="https://x/other.jpg"
        )
        older = VerificationCredential.objects.create(
            user=user, document_type="licence", document_url="https://x/older.jpg"
        )
        newer = VerificationCredential.objects.create(
            user=user, document_type="degree", document_url="https://x/newer.jpg"
        )
        # auto_now_add fields ignore assignment through .save(); go
        # through .update() to force a distinct order — two rows created
        # back-to-back can otherwise land in the same clock tick, same
        # backdating pattern tests/apps/build_log/test_views.py uses.
        VerificationCredential.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(minutes=5)
        )

        response = api_client.get(_me_url())
        assert response.status_code == 200
        ids = [row["id"] for row in response.data]
        assert ids == [str(newer.id), str(older.id)]


@pytest.mark.django_db
class TestVerificationCredentialAdminCascade:
    """Session build-log/verification-hub work: approval cascades to
    User.is_verified; rejection deliberately does not un-verify.
    """

    def _admin(self):
        return VerificationCredentialAdmin(VerificationCredential, django_admin.site)

    def test_approve_action_sets_user_is_verified(self):
        user = _make_user("admin-approve@example.com")
        admin_user = _make_user("admin-reviewer@example.com", is_staff=True)
        credential = VerificationCredential.objects.create(
            user=user, document_type="licence", document_url="https://x/doc.jpg"
        )
        assert user.is_verified is False

        request = MagicMock(user=admin_user)
        self._admin().approve_credentials(request, VerificationCredential.objects.filter(pk=credential.pk))

        credential.refresh_from_db()
        user.refresh_from_db()
        assert credential.status == CredentialStatus.APPROVED
        assert credential.reviewed_by == admin_user
        assert user.is_verified is True

    def test_reject_action_does_not_touch_is_verified(self):
        user = _make_user("admin-reject@example.com")
        admin_user = _make_user("admin-reviewer2@example.com", is_staff=True)
        credential = VerificationCredential.objects.create(
            user=user, document_type="licence", document_url="https://x/doc.jpg"
        )

        request = MagicMock(user=admin_user)
        self._admin().reject_credentials(request, VerificationCredential.objects.filter(pk=credential.pk))

        credential.refresh_from_db()
        user.refresh_from_db()
        assert credential.status == CredentialStatus.REJECTED
        assert user.is_verified is False

    def test_rejecting_a_different_credential_does_not_unverify_already_verified_user(self):
        # Locked-in decision: badge is earned-once, never auto-revoked by
        # an unrelated rejected submission.
        user = _make_user("admin-already-verified@example.com", is_verified=True)
        admin_user = _make_user("admin-reviewer3@example.com", is_staff=True)
        second_credential = VerificationCredential.objects.create(
            user=user, document_type="membership", document_url="https://x/doc2.jpg"
        )

        request = MagicMock(user=admin_user)
        self._admin().reject_credentials(
            request, VerificationCredential.objects.filter(pk=second_credential.pk)
        )

        user.refresh_from_db()
        assert user.is_verified is True
