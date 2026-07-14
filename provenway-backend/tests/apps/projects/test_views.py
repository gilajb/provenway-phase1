import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.projects.models import (
    Project,
    ProjectDiscipline,
    ProjectStatus,
    ProjectVisibility,
)


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
    project = Project.objects.create(owner=owner, **kwargs)
    return project


@pytest.mark.django_db
class TestBannedOwnerContentHidden:
    """Session 16 permission audit: a deactivated/banned owner
    (is_active=False) was already hidden from PublicProfileView and
    directory search, but their projects kept appearing via project
    list/detail and (transitively) the feed — a moderation bypass. These
    lock in the fix in apps.projects.permissions.
    """

    def test_banned_owners_public_project_excluded_from_anonymous_list(self, api_client):
        banned = _make_user("banned-list-anon@example.com", is_active=False)
        _make_project(banned, title="Ghost Tower", visibility=ProjectVisibility.PUBLIC)
        response = api_client.get(reverse("projects:list-create"))
        titles = [p["title"] for p in response.data["results"]]
        assert "Ghost Tower" not in titles

    def test_banned_owners_public_project_excluded_from_authenticated_list(self, api_client):
        banned = _make_user("banned-list-auth@example.com", is_active=False)
        viewer = _make_user("viewer-banned-list@example.com")
        _make_project(banned, title="Ghost Tower 2", visibility=ProjectVisibility.PUBLIC)
        _auth(api_client, viewer)
        response = api_client.get(reverse("projects:list-create"))
        titles = [p["title"] for p in response.data["results"]]
        assert "Ghost Tower 2" not in titles

    def test_banned_owners_public_project_detail_returns_404(self, api_client):
        banned = _make_user("banned-detail@example.com", is_active=False)
        project = _make_project(banned, visibility=ProjectVisibility.PUBLIC)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_banned_owners_public_project_detail_404_even_when_authenticated(self, api_client):
        banned = _make_user("banned-detail2@example.com", is_active=False)
        viewer = _make_user("viewer-banned-detail@example.com")
        project = _make_project(banned, visibility=ProjectVisibility.PUBLIC)
        _auth(api_client, viewer)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_project_disappears_from_list_once_owner_is_banned(self, api_client):
        # Same account, before/after a ban — proves this is enforced at
        # read time, not just for accounts created already-banned.
        owner = _make_user("soon-banned@example.com")
        _make_project(owner, title="About To Vanish", visibility=ProjectVisibility.PUBLIC)

        before = api_client.get(reverse("projects:list-create"))
        assert "About To Vanish" in [p["title"] for p in before.data["results"]]

        owner.is_active = False
        owner.save(update_fields=["is_active"])

        after = api_client.get(reverse("projects:list-create"))
        assert "About To Vanish" not in [p["title"] for p in after.data["results"]]



    def test_create_requires_authentication(self, api_client):
        response = api_client.post(
            reverse("projects:list-create"), {"title": "New Project"}, format="json"
        )
        assert response.status_code == 401

    def test_authenticated_user_can_create_project(self, api_client):
        user = _make_user("owner@example.com")
        _auth(api_client, user)
        payload = {
            "title": "Nairobi Highrise",
            "description": "20-storey mixed-use tower",
            "location_text": "Westlands, Nairobi",
            "status": "active",
            "visibility": "public",
            "disciplines": ["structural_engineer", "civil_engineer"],
        }
        response = api_client.post(
            reverse("projects:list-create"), payload, format="json"
        )
        assert response.status_code == 201
        assert response.data["title"] == "Nairobi Highrise"
        assert set(response.data["disciplines"]) == {
            "structural_engineer",
            "civil_engineer",
        }
        assert response.data["owner"]["id"] == str(user.id)
        assert response.data["is_owner"] is True

        project = Project.objects.get(id=response.data["id"])
        assert project.owner_id == user.id
        assert ProjectDiscipline.objects.filter(project=project).count() == 2

    def test_created_project_defaults_created_at_server_set(self, api_client):
        user = _make_user("owner2@example.com")
        _auth(api_client, user)
        response = api_client.post(
            reverse("projects:list-create"),
            {"title": "Test Project", "created_at": "2000-01-01T00:00:00Z"},
            format="json",
        )
        assert response.status_code == 201
        project = Project.objects.get(id=response.data["id"])
        assert project.created_at.year != 2000  # client-supplied value ignored


@pytest.mark.django_db
class TestProjectList:
    def test_anonymous_sees_only_public_projects(self, api_client):
        owner = _make_user("owner3@example.com")
        _make_project(owner, title="Public One", visibility=ProjectVisibility.PUBLIC)
        _make_project(owner, title="Private One", visibility=ProjectVisibility.PRIVATE)
        _make_project(
            owner, title="Connections One", visibility=ProjectVisibility.CONNECTIONS
        )

        response = api_client.get(reverse("projects:list-create"))
        assert response.status_code == 200
        titles = {p["title"] for p in response.data["results"]}
        assert titles == {"Public One"}

    def test_owner_sees_all_own_projects_regardless_of_visibility(self, api_client):
        owner = _make_user("owner4@example.com")
        _make_project(owner, title="Public One", visibility=ProjectVisibility.PUBLIC)
        _make_project(owner, title="Private One", visibility=ProjectVisibility.PRIVATE)
        _make_project(
            owner, title="Connections One", visibility=ProjectVisibility.CONNECTIONS
        )
        _auth(api_client, owner)

        response = api_client.get(reverse("projects:list-create"))
        titles = {p["title"] for p in response.data["results"]}
        assert titles == {"Public One", "Private One", "Connections One"}

    def test_other_authenticated_user_cannot_see_private_or_connections_projects(
        self, api_client
    ):
        owner = _make_user("owner5@example.com")
        other = _make_user("other5@example.com")
        _make_project(owner, title="Public One", visibility=ProjectVisibility.PUBLIC)
        _make_project(owner, title="Private One", visibility=ProjectVisibility.PRIVATE)
        _make_project(
            owner, title="Connections One", visibility=ProjectVisibility.CONNECTIONS
        )
        _auth(api_client, other)

        response = api_client.get(reverse("projects:list-create"))
        titles = {p["title"] for p in response.data["results"]}
        assert titles == {"Public One"}

    def test_soft_deleted_project_never_appears_in_list(self, api_client):
        owner = _make_user("owner6@example.com")
        project = _make_project(
            owner, title="Doomed Project", visibility=ProjectVisibility.PUBLIC
        )
        project.soft_delete()
        _auth(api_client, owner)

        response = api_client.get(reverse("projects:list-create"))
        titles = {p["title"] for p in response.data["results"]}
        assert "Doomed Project" not in titles
        # sanity: row still exists in the DB, just excluded by the manager
        assert Project.all_objects.filter(id=project.id, is_deleted=True).exists()

    def test_filter_by_discipline(self, api_client):
        owner = _make_user("owner7@example.com")
        p1 = _make_project(owner, title="Civil Job")
        ProjectDiscipline.objects.create(project=p1, discipline="civil_engineer")
        p2 = _make_project(owner, title="Architecture Job")
        ProjectDiscipline.objects.create(project=p2, discipline="architect")

        response = api_client.get(
            reverse("projects:list-create"), {"discipline": "civil_engineer"}
        )
        titles = {p["title"] for p in response.data["results"]}
        assert titles == {"Civil Job"}

    def test_filter_by_status(self, api_client):
        owner = _make_user("owner8@example.com")
        _make_project(owner, title="Active Job", status=ProjectStatus.ACTIVE)
        _make_project(owner, title="Paused Job", status=ProjectStatus.PAUSED)

        response = api_client.get(reverse("projects:list-create"), {"status": "paused"})
        titles = {p["title"] for p in response.data["results"]}
        assert titles == {"Paused Job"}

    def test_filter_by_location(self, api_client):
        owner = _make_user("owner9@example.com")
        _make_project(owner, title="Nairobi Job", location_text="Nairobi, Kenya")
        _make_project(owner, title="Mombasa Job", location_text="Mombasa, Kenya")

        response = api_client.get(
            reverse("projects:list-create"), {"location": "nairobi"}
        )
        titles = {p["title"] for p in response.data["results"]}
        assert titles == {"Nairobi Job"}


@pytest.mark.django_db
class TestProjectDetail:
    def test_anonymous_can_view_public_project(self, api_client):
        owner = _make_user("owner10@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 200
        assert response.data["title"] == project.title

    def test_anonymous_gets_404_for_private_project(self, api_client):
        owner = _make_user("owner11@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_non_owner_gets_404_for_private_project(self, api_client):
        owner = _make_user("owner12@example.com")
        other = _make_user("other12@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        _auth(api_client, other)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_owner_can_view_own_private_project(self, api_client):
        owner = _make_user("owner13@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PRIVATE)
        _auth(api_client, owner)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 200

    def test_non_owner_gets_404_for_connections_only_project(self, api_client):
        # apps.networking.Follow now exists (this session), and the
        # CONNECTIONS branch of user_can_view_project is a real
        # mutual-follow check rather than the old owner-only TODO stub —
        # this test still locks in that a viewer with *no* follow
        # relationship to the owner at all never sees a connections-only
        # project leak through.
        owner = _make_user("owner14@example.com")
        other = _make_user("other14@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.CONNECTIONS)
        _auth(api_client, other)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_one_directional_follower_still_gets_404_for_connections_only_project(
        self, api_client
    ):
        # `other` follows `owner`, but `owner` doesn't follow back — per
        # apps.projects.permissions._is_mutual_connection, a one-directional
        # follow is NOT a "connection" (Engineering Doc §1.4.1: mutual
        # follow = connection), so this must still 404.
        from apps.networking.models import Follow

        owner = _make_user("owner14b@example.com")
        other = _make_user("other14b@example.com")
        Follow.objects.create(follower=other, following=owner)
        project = _make_project(owner, visibility=ProjectVisibility.CONNECTIONS)
        _auth(api_client, other)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_one_directional_followed_by_owner_still_gets_404_for_connections_only_project(
        self, api_client
    ):
        # Reverse direction: `owner` follows `other`, but `other` doesn't
        # follow back. Still not mutual, still 404.
        from apps.networking.models import Follow

        owner = _make_user("owner14c@example.com")
        other = _make_user("other14c@example.com")
        Follow.objects.create(follower=owner, following=other)
        project = _make_project(owner, visibility=ProjectVisibility.CONNECTIONS)
        _auth(api_client, other)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_mutual_connection_can_view_connections_only_project(self, api_client):
        # `owner` and `other` follow each other — a real connection per
        # Engineering Doc §1.4.1 — so `other` should now see it.
        from apps.networking.models import Follow

        owner = _make_user("owner14d@example.com")
        other = _make_user("other14d@example.com")
        Follow.objects.create(follower=owner, following=other)
        Follow.objects.create(follower=other, following=owner)
        project = _make_project(owner, visibility=ProjectVisibility.CONNECTIONS)
        _auth(api_client, other)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 200
        assert response.data["title"] == project.title

    def test_mutual_connection_sees_connections_only_project_in_list(self, api_client):
        from apps.networking.models import Follow

        owner = _make_user("owner14e@example.com")
        other = _make_user("other14e@example.com")
        Follow.objects.create(follower=owner, following=other)
        Follow.objects.create(follower=other, following=owner)
        _make_project(
            owner, title="Connections Visible", visibility=ProjectVisibility.CONNECTIONS
        )
        _make_project(
            owner, title="Still Private", visibility=ProjectVisibility.PRIVATE
        )
        _auth(api_client, other)

        response = api_client.get(reverse("projects:list-create"))
        titles = {p["title"] for p in response.data["results"]}
        assert "Connections Visible" in titles
        assert "Still Private" not in titles

    def test_non_mutual_follower_does_not_see_connections_only_project_in_list(
        self, api_client
    ):
        from apps.networking.models import Follow

        owner = _make_user("owner14f@example.com")
        other = _make_user("other14f@example.com")
        Follow.objects.create(follower=other, following=owner)  # one-directional only
        _make_project(
            owner, title="Connections Hidden", visibility=ProjectVisibility.CONNECTIONS
        )
        _auth(api_client, other)

        response = api_client.get(reverse("projects:list-create"))
        titles = {p["title"] for p in response.data["results"]}
        assert "Connections Hidden" not in titles

    def test_soft_deleted_project_returns_404_even_to_owner(self, api_client):
        owner = _make_user("owner15@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        project.soft_delete()
        _auth(api_client, owner)
        response = api_client.get(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 404

    def test_nonexistent_project_returns_404(self, api_client):
        import uuid

        response = api_client.get(reverse("projects:detail", args=[uuid.uuid4()]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectUpdate:
    def test_owner_can_patch_own_project(self, api_client):
        owner = _make_user("owner16@example.com")
        project = _make_project(owner, title="Old Title")
        _auth(api_client, owner)
        response = api_client.patch(
            reverse("projects:detail", args=[project.id]),
            {"title": "New Title"},
            format="json",
        )
        assert response.status_code == 200
        project.refresh_from_db()
        assert project.title == "New Title"

    def test_non_owner_cannot_patch_public_project(self, api_client):
        owner = _make_user("owner17@example.com")
        other = _make_user("other17@example.com")
        project = _make_project(
            owner, title="Old Title", visibility=ProjectVisibility.PUBLIC
        )
        _auth(api_client, other)
        response = api_client.patch(
            reverse("projects:detail", args=[project.id]),
            {"title": "Hacked"},
            format="json",
        )
        assert response.status_code == 403
        project.refresh_from_db()
        assert project.title == "Old Title"

    def test_anonymous_cannot_patch(self, api_client):
        owner = _make_user("owner18@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        response = api_client.patch(
            reverse("projects:detail", args=[project.id]),
            {"title": "Hacked"},
            format="json",
        )
        assert response.status_code == 401

    def test_patch_replaces_disciplines(self, api_client):
        owner = _make_user("owner19@example.com")
        project = _make_project(owner)
        ProjectDiscipline.objects.create(project=project, discipline="architect")
        _auth(api_client, owner)
        response = api_client.patch(
            reverse("projects:detail", args=[project.id]),
            {"disciplines": ["qs", "contractor"]},
            format="json",
        )
        assert response.status_code == 200
        assert set(response.data["disciplines"]) == {"qs", "contractor"}
        assert ProjectDiscipline.objects.filter(project=project).count() == 2


@pytest.mark.django_db
class TestProjectDelete:
    def test_owner_delete_soft_deletes_not_hard_deletes(self, api_client):
        owner = _make_user("owner20@example.com")
        project = _make_project(owner)
        _auth(api_client, owner)
        response = api_client.delete(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 204

        # row still exists, just flagged
        row = Project.all_objects.get(id=project.id)
        assert row.is_deleted is True
        assert row.deleted_at is not None

    def test_non_owner_cannot_delete(self, api_client):
        owner = _make_user("owner21@example.com")
        other = _make_user("other21@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        _auth(api_client, other)
        response = api_client.delete(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 403
        assert Project.objects.filter(id=project.id, is_deleted=False).exists()

    def test_anonymous_cannot_delete(self, api_client):
        owner = _make_user("owner22@example.com")
        project = _make_project(owner, visibility=ProjectVisibility.PUBLIC)
        response = api_client.delete(reverse("projects:detail", args=[project.id]))
        assert response.status_code == 401
