import io
import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.build_log.models import MAX_PHOTOS_PER_UPDATE, ProjectUpdate, UpdatePhoto
from apps.projects.models import Project, ProjectStatus, ProjectVisibility


@pytest.fixture
def api_client():
    return APIClient()


def _make_user(email, **kwargs):
    kwargs.setdefault("display_name", "Test User")
    kwargs.setdefault("is_email_verified", True)
    return User.objects.create_user(email=email, password="StrongPass1", **kwargs)


def _auth(api_client, user):
    api_client.force_authenticate(user=user)


def _make_project(owner, **kwargs):
    kwargs.setdefault("title", "Riverside Apartments")
    kwargs.setdefault("visibility", ProjectVisibility.PUBLIC)
    kwargs.setdefault("status", ProjectStatus.ACTIVE)
    return Project.objects.create(owner=owner, **kwargs)


def _make_update(project, author, **kwargs):
    kwargs.setdefault("title", "Foundation poured")
    kwargs.setdefault("entry_type", "milestone")
    kwargs.setdefault("entry_date", "2026-06-01")
    return ProjectUpdate.objects.create(project=project, author=author, **kwargs)


def _set_created_at(update, when):
    # auto_now_add fields ignore assignment through .save(); go through
    # .update() to backdate for edit-window boundary tests.
    ProjectUpdate.objects.filter(pk=update.pk).update(created_at=when)
    update.refresh_from_db()


def _tiny_jpeg_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _uploaded_photo(name="photo.jpg"):
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(name, _tiny_jpeg_bytes(), content_type="image/jpeg")


def _list_url(project_id):
    return reverse("build_log:update-list-create", args=[project_id])


def _detail_url(project_id, update_id):
    return reverse("build_log:update-detail", args=[project_id, update_id])


def _photos_url(project_id, update_id):
    return reverse("build_log:update-photo-upload", args=[project_id, update_id])


@pytest.mark.django_db
class TestProjectUpdateCreate:
    def test_create_requires_authentication(self, api_client):
        owner = _make_user("owner1@example.com")
        project = _make_project(owner)
        response = api_client.post(
            _list_url(project.id),
            {"title": "Slab cast", "entry_type": "milestone", "entry_date": "2026-06-01"},
            format="json",
        )
        assert response.status_code == 401

    def test_owner_can_create_update(self, api_client):
        owner = _make_user("owner2@example.com")
        project = _make_project(owner)
        _auth(api_client, owner)
        payload = {
            "title": "Slab cast",
            "body": "<script>alert(1)</script><p>Poured the ground floor slab.</p>",
            "entry_type": "milestone",
            "entry_date": "2026-06-01",
        }
        response = api_client.post(_list_url(project.id), payload, format="json")
        assert response.status_code == 201
        assert response.data["title"] == "Slab cast"
        assert response.data["author"]["id"] == str(owner.id)
        assert response.data["project"] == str(project.id)
        assert response.data["is_editable"] is True
        # sanitisation strips disallowed tags (script) but keeps whitelisted ones
        assert "<script>" not in response.data["body"]
        assert "<p>" in response.data["body"]

    def test_non_owner_cannot_create_update_on_public_project(self, api_client):
        owner = _make_user("owner3@example.com")
        other = _make_user("other3@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        _auth(api_client, other)
        response = api_client.post(
            _list_url(project.id),
            {"title": "Hacked entry", "entry_type": "milestone", "entry_date": "2026-06-01"},
            format="json",
        )
        assert response.status_code == 403
        assert not ProjectUpdate.objects.filter(project=project).exists()

    def test_non_owner_gets_404_creating_on_private_project(self, api_client):
        owner = _make_user("owner4@example.com")
        other = _make_user("other4@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        _auth(api_client, other)
        response = api_client.post(
            _list_url(project.id),
            {"title": "Hacked entry", "entry_type": "milestone", "entry_date": "2026-06-01"},
            format="json",
        )
        assert response.status_code == 404

    def test_created_at_is_server_set_not_client_set(self, api_client):
        owner = _make_user("owner5@example.com")
        project = _make_project(owner)
        _auth(api_client, owner)
        response = api_client.post(
            _list_url(project.id),
            {
                "title": "Slab cast",
                "entry_type": "milestone",
                "entry_date": "2026-06-01",
                "created_at": "2000-01-01T00:00:00Z",
            },
            format="json",
        )
        assert response.status_code == 201
        update = ProjectUpdate.objects.get(id=response.data["id"])
        assert update.created_at.year != 2000

    def test_create_404_on_nonexistent_project(self, api_client):
        owner = _make_user("owner6@example.com")
        _auth(api_client, owner)
        response = api_client.post(
            _list_url(uuid.uuid4()),
            {"title": "x", "entry_type": "milestone", "entry_date": "2026-06-01"},
            format="json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectUpdateList:
    def test_anonymous_can_list_updates_on_public_project(self, api_client):
        owner = _make_user("owner7@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        _make_update(project, owner, title="Update A")
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 200
        titles = {u["title"] for u in response.data["results"]}
        assert titles == {"Update A"}

    def test_anonymous_gets_404_listing_updates_on_private_project(self, api_client):
        owner = _make_user("owner8@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        _make_update(project, owner)
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 404

    def test_non_owner_gets_404_listing_updates_on_private_project(self, api_client):
        owner = _make_user("owner9@example.com")
        other = _make_user("other9@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        _make_update(project, owner)
        _auth(api_client, other)
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 404

    def test_non_owner_gets_404_listing_updates_on_connections_project(self, api_client):
        # No Follow model yet (apps.networking not scaffolded) — connections
        # visibility collapses to owner-only, matching apps.projects'
        # existing behaviour. This locks in that updates never leak through
        # this endpoint even though the parent Project check does.
        owner = _make_user("owner10@example.com")
        other = _make_user("other10@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.CONNECTIONS)
        _make_update(project, owner)
        _auth(api_client, other)
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 404

    def test_updates_on_soft_deleted_project_return_404(self, api_client):
        owner = _make_user("owner11@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        _make_update(project, owner)
        project.soft_delete()
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 404

    def test_owner_sees_own_private_project_updates(self, api_client):
        owner = _make_user("owner12@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        _make_update(project, owner, title="Private update")
        _auth(api_client, owner)
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 200
        titles = {u["title"] for u in response.data["results"]}
        assert titles == {"Private update"}

    def test_updates_on_banned_owners_project_return_404(self, api_client):
        # Session 16 permission audit: build-log updates inherit
        # visibility from their parent Project, which now excludes
        # deactivated/banned owners — locks that in through this
        # endpoint too, not just apps.projects' own.
        banned = _make_user("banned-updates-owner@example.com", is_active=False)
        project = _make_project(banned, visibility=ProjectVisibility.PUBLIC)
        _make_update(project, banned)
        response = api_client.get(_list_url(project.id))
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectUpdateDetail:
    def test_anonymous_gets_404_for_update_on_private_project(self, api_client):
        owner = _make_user("owner13@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        update = _make_update(project, owner)
        response = api_client.get(_detail_url(project.id, update.id))
        assert response.status_code == 404

    def test_anonymous_can_view_update_on_public_project(self, api_client):
        owner = _make_user("owner14@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        update = _make_update(project, owner)
        response = api_client.get(_detail_url(project.id, update.id))
        assert response.status_code == 200
        assert response.data["id"] == str(update.id)

    def test_soft_deleted_update_returns_404(self, api_client):
        owner = _make_user("owner15@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        update = _make_update(project, owner)
        update.soft_delete()
        response = api_client.get(_detail_url(project.id, update.id))
        assert response.status_code == 404

    def test_nonexistent_update_returns_404(self, api_client):
        owner = _make_user("owner16@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        response = api_client.get(_detail_url(project.id, uuid.uuid4()))
        assert response.status_code == 404

    def test_update_from_wrong_project_returns_404(self, api_client):
        # Guards against /projects/{A}/updates/{uid}/ resolving an update
        # that actually belongs to project B.
        owner = _make_user("owner17@example.com")
        project_a = _make_project(owner, title="Project A", visibility=ProjectVisibility.PUBLIC)
        project_b = _make_project(owner, title="Project B", visibility=ProjectVisibility.PUBLIC)
        update = _make_update(project_b, owner)
        response = api_client.get(_detail_url(project_a.id, update.id))
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectUpdateEditWindow:
    def test_owner_can_patch_within_edit_window(self, api_client):
        owner = _make_user("owner18@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner, title="Old title")
        _set_created_at(update, timezone.now() - timedelta(hours=23, minutes=59))
        _auth(api_client, owner)
        response = api_client.patch(
            _detail_url(project.id, update.id), {"title": "New title"}, format="json"
        )
        assert response.status_code == 200
        update.refresh_from_db()
        assert update.title == "New title"

    def test_owner_cannot_patch_just_outside_edit_window(self, api_client):
        owner = _make_user("owner19@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner, title="Old title")
        _set_created_at(update, timezone.now() - timedelta(hours=24, minutes=1))
        _auth(api_client, owner)
        response = api_client.patch(
            _detail_url(project.id, update.id), {"title": "New title"}, format="json"
        )
        assert response.status_code == 403
        update.refresh_from_db()
        assert update.title == "Old title"

    def test_owner_cannot_patch_exactly_at_boundary(self, api_client):
        owner = _make_user("owner20@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner, title="Old title")
        _set_created_at(update, timezone.now() - timedelta(hours=24))
        _auth(api_client, owner)
        response = api_client.patch(
            _detail_url(project.id, update.id), {"title": "New title"}, format="json"
        )
        assert response.status_code == 403
        update.refresh_from_db()
        assert update.title == "Old title"

    def test_non_owner_cannot_patch_even_within_window(self, api_client):
        owner = _make_user("owner21@example.com")
        other = _make_user("other21@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        update = _make_update(project, owner, title="Old title")
        _auth(api_client, other)
        response = api_client.patch(
            _detail_url(project.id, update.id), {"title": "Hacked"}, format="json"
        )
        assert response.status_code == 403
        update.refresh_from_db()
        assert update.title == "Old title"

    def test_delete_has_no_edit_window_restriction(self, api_client):
        owner = _make_user("owner22@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        _set_created_at(update, timezone.now() - timedelta(days=10))
        _auth(api_client, owner)
        response = api_client.delete(_detail_url(project.id, update.id))
        assert response.status_code == 204
        row = ProjectUpdate.all_objects.get(id=update.id)
        assert row.is_deleted is True
        assert row.deleted_at is not None

    def test_non_owner_cannot_delete(self, api_client):
        owner = _make_user("owner23@example.com")
        other = _make_user("other23@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        update = _make_update(project, owner)
        _auth(api_client, other)
        response = api_client.delete(_detail_url(project.id, update.id))
        assert response.status_code == 403
        assert ProjectUpdate.objects.filter(id=update.id).exists()


@pytest.mark.django_db
class TestUpdatePhotoUpload:
    def test_requires_authentication(self, api_client):
        owner = _make_user("owner24@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": [_uploaded_photo()]}, format="multipart"
        )
        assert response.status_code == 401

    def test_non_owner_cannot_upload_photos(self, api_client):
        owner = _make_user("owner25@example.com")
        other = _make_user("other25@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        update = _make_update(project, owner)
        _auth(api_client, other)
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": [_uploaded_photo()]}, format="multipart"
        )
        assert response.status_code == 403
        assert UpdatePhoto.objects.filter(update=update).count() == 0

    @patch("apps.build_log.views.upload_update_photo")
    def test_owner_can_upload_photos(self, mock_upload, api_client):
        mock_upload.side_effect = lambda file_obj, update_id, sequence_order: {
            "public_id": f"provenway/updates/{update_id}/photo_{sequence_order}",
            "secure_url": f"https://cdn.example.com/photo_{sequence_order}.jpg",
        }
        owner = _make_user("owner26@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        _auth(api_client, owner)
        response = api_client.post(
            _photos_url(project.id, update.id),
            {"photos": [_uploaded_photo("a.jpg"), _uploaded_photo("b.jpg")]},
            format="multipart",
        )
        assert response.status_code == 201
        assert len(response.data) == 2
        photos = list(UpdatePhoto.objects.filter(update=update).order_by("sequence_order"))
        assert [p.sequence_order for p in photos] == [0, 1]

    @patch("apps.build_log.views.upload_update_photo")
    def test_ten_photo_cap_enforced_in_single_request(self, mock_upload, api_client):
        mock_upload.side_effect = lambda file_obj, update_id, sequence_order: {
            "public_id": f"photo_{sequence_order}",
            "secure_url": f"https://cdn.example.com/photo_{sequence_order}.jpg",
        }
        owner = _make_user("owner27@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        _auth(api_client, owner)
        too_many = [_uploaded_photo(f"p{i}.jpg") for i in range(11)]
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": too_many}, format="multipart"
        )
        assert response.status_code == 400
        assert UpdatePhoto.objects.filter(update=update).count() == 0

    @patch("apps.build_log.views.upload_update_photo")
    def test_ten_photo_cap_enforced_across_multiple_requests(self, mock_upload, api_client):
        mock_upload.side_effect = lambda file_obj, update_id, sequence_order: {
            "public_id": f"photo_{sequence_order}",
            "secure_url": f"https://cdn.example.com/photo_{sequence_order}.jpg",
        }
        owner = _make_user("owner28@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        _auth(api_client, owner)

        first_batch = [_uploaded_photo(f"p{i}.jpg") for i in range(MAX_PHOTOS_PER_UPDATE)]
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": first_batch}, format="multipart"
        )
        assert response.status_code == 201
        assert UpdatePhoto.objects.filter(update=update).count() == MAX_PHOTOS_PER_UPDATE

        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": [_uploaded_photo("overflow.jpg")]},
            format="multipart",
        )
        assert response.status_code == 400
        assert UpdatePhoto.objects.filter(update=update).count() == MAX_PHOTOS_PER_UPDATE

    @patch("apps.build_log.views.upload_update_photo")
    def test_photos_rejects_non_image_file(self, mock_upload, api_client):
        from django.core.files.uploadedfile import SimpleUploadedFile

        owner = _make_user("owner29@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        _auth(api_client, owner)
        bad_file = SimpleUploadedFile("not-an-image.txt", b"hello world", content_type="text/plain")
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": [bad_file]}, format="multipart"
        )
        assert response.status_code == 400
        mock_upload.assert_not_called()

    def test_upload_404_on_private_project_for_non_owner(self, api_client):
        owner = _make_user("owner30@example.com")
        other = _make_user("other30@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        update = _make_update(project, owner)
        _auth(api_client, other)
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": [_uploaded_photo()]}, format="multipart"
        )
        assert response.status_code == 404

    @patch("apps.build_log.views.upload_update_photo")
    def test_exif_extracted_into_update_metadata_when_present(self, mock_upload, api_client):
        mock_upload.side_effect = lambda file_obj, update_id, sequence_order: {
            "public_id": f"photo_{sequence_order}",
            "secure_url": f"https://cdn.example.com/photo_{sequence_order}.jpg",
        }
        owner = _make_user("owner31@example.com")
        project = _make_project(owner)
        update = _make_update(project, owner)
        _auth(api_client, owner)

        # A plain generated JPEG carries no EXIF block — this asserts the
        # no-EXIF path doesn't error and simply leaves exif_metadata empty,
        # which is the realistic case for our test fixture image.
        response = api_client.post(
            _photos_url(project.id, update.id), {"photos": [_uploaded_photo()]}, format="multipart"
        )
        assert response.status_code == 201
        update.refresh_from_db()
        assert update.exif_metadata is None


@pytest.mark.django_db
class TestUpdatePhotoUploadRateLimit:
    """Session 16 permission audit, item 5: photo upload had no rate
    limiting at all — regression test for the fix in
    apps.build_log.views.UpdatePhotoUploadView.
    """

    @patch("apps.build_log.views.upload_update_photo")
    def test_exceeding_rate_limit_returns_429(self, mock_upload, api_client):
        from django.core.cache import cache
        from django.test import override_settings

        mock_upload.side_effect = lambda file_obj, update_id, sequence_order: {
            "public_id": f"photo_{sequence_order}",
            "secure_url": f"https://cdn.example.com/photo_{sequence_order}.jpg",
        }
        owner = _make_user("ratelimited-photo-owner@example.com")
        _auth(api_client, owner)
        cache.clear()

        # A fresh update per call sidesteps the 10-photo-per-update cap
        # so the rate limit itself is what trips the 31st request.
        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for _ in range(31):  # limit is 30/h
                project = _make_project(owner, title=f"Proj {_}")
                update = _make_update(project, owner)
                last_response = api_client.post(
                    _photos_url(project.id, update.id),
                    {"photos": [_uploaded_photo()]},
                    format="multipart",
                )
            assert last_response.status_code == 429
        cache.clear()
