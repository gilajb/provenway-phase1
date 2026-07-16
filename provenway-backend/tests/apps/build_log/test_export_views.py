from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.build_log.models import ProjectUpdate
from apps.build_log.tasks import generate_project_pdf_task
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


def _export_url(project_id):
    return reverse("build_log:export-pdf", args=[project_id])


def _task_status_url(task_id):
    return reverse("task-status", args=[task_id])


@pytest.mark.django_db
class TestProjectExportView:
    def test_requires_authentication(self, api_client):
        owner = _make_user("owner-noauth@example.com")
        project = _make_project(owner)
        response = api_client.post(_export_url(project.id))
        assert response.status_code == 401

    @patch("apps.build_log.views.generate_project_pdf_task")
    def test_owner_can_trigger_export(self, mock_task, api_client):
        owner = _make_user("owner-export@example.com")
        project = _make_project(owner)
        _auth(api_client, owner)

        mock_task.delay.return_value = MagicMock(id="fake-task-id-123")
        response = api_client.post(_export_url(project.id))

        assert response.status_code == 202
        assert response.data["task_id"] == "fake-task-id-123"
        mock_task.delay.assert_called_once_with(str(project.id))

    @patch("apps.build_log.views.generate_project_pdf_task")
    def test_non_owner_forbidden(self, mock_task, api_client):
        owner = _make_user("owner-forbidden@example.com")
        other = _make_user("other-forbidden@example.com")
        project = _make_project(owner)
        _auth(api_client, other)

        response = api_client.post(_export_url(project.id))
        assert response.status_code == 403
        mock_task.delay.assert_not_called()

    def test_nonexistent_project_404(self, api_client):
        import uuid

        user = _make_user("owner-404@example.com")
        _auth(api_client, user)
        response = api_client.post(_export_url(uuid.uuid4()))
        assert response.status_code == 404

    @patch("apps.build_log.views.generate_project_pdf_task")
    def test_rate_limit_returns_429_after_five_per_hour(self, mock_task, api_client):
        from django.core.cache import cache
        from django.test import override_settings

        owner = _make_user("owner-ratelimit@example.com")
        projects = [_make_project(owner, title=f"Project {i}") for i in range(6)]
        _auth(api_client, owner)
        mock_task.delay.return_value = MagicMock(id="task-id")
        cache.clear()

        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for project in projects:  # limit is 5/h
                last_response = api_client.post(_export_url(project.id))
            assert last_response.status_code == 429
        cache.clear()


@pytest.mark.django_db
class TestProjectExportStatusView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(_task_status_url("some-task-id"))
        assert response.status_code == 401

    @patch("apps.build_log.views.AsyncResult")
    def test_pending_task_reports_processing(self, mock_async_result, api_client):
        user = _make_user("status-pending@example.com")
        _auth(api_client, user)
        mock_async_result.return_value = MagicMock(state="PENDING")

        response = api_client.get(_task_status_url("task-1"))
        assert response.status_code == 200
        assert response.data["status"] == "processing"

    @patch("apps.build_log.views.AsyncResult")
    def test_successful_task_returns_pdf_url(self, mock_async_result, api_client):
        user = _make_user("status-success@example.com")
        _auth(api_client, user)
        mock_async_result.return_value = MagicMock(
            state="SUCCESS", result={"pdf_url": "https://res.cloudinary.com/x/export.pdf"}
        )

        response = api_client.get(_task_status_url("task-2"))
        assert response.status_code == 200
        assert response.data["status"] == "completed"
        assert response.data["pdf_url"] == "https://res.cloudinary.com/x/export.pdf"

    @patch("apps.build_log.views.AsyncResult")
    def test_failed_task_returns_clean_error_not_raw_exception(self, mock_async_result, api_client):
        user = _make_user("status-failed@example.com")
        _auth(api_client, user)
        mock_async_result.return_value = MagicMock(
            state="FAILURE", result=RuntimeError("some internal traceback detail")
        )

        response = api_client.get(_task_status_url("task-3"))
        assert response.status_code == 200
        assert response.data["status"] == "failed"
        assert "traceback" not in response.data["error"]


@pytest.mark.django_db
class TestGenerateProjectPdfTask:
    @patch("apps.build_log.tasks.upload_export_pdf")
    @patch("apps.build_log.tasks.build_portfolio_pdf")
    def test_success_returns_pdf_url(self, mock_build, mock_upload):
        owner = _make_user("task-success@example.com")
        project = _make_project(owner)
        mock_build.return_value = b"%PDF-fake-bytes"
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/x/export.pdf"}

        result = generate_project_pdf_task(str(project.id))

        assert result == {"pdf_url": "https://res.cloudinary.com/x/export.pdf"}
        mock_build.assert_called_once()
        mock_upload.assert_called_once_with(b"%PDF-fake-bytes", str(project.id))

    def test_missing_project_raises_immediately(self):
        import uuid

        with pytest.raises(Project.DoesNotExist):
            generate_project_pdf_task(str(uuid.uuid4()))
