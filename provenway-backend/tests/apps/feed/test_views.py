import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.authentication.models import User
from apps.build_log.models import ProjectUpdate
from apps.networking.models import Follow
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
    # auto_now_add ignores assignment through .save(); go through
    # .update() to control ordering deterministically for pagination tests
    # — mirrors tests/apps/build_log/test_views.py's _set_created_at.
    ProjectUpdate.objects.filter(pk=update.pk).update(created_at=when)
    update.refresh_from_db()


def _feed_url():
    return reverse("feed:feed-list")


@pytest.mark.django_db
class TestFeedAuth:
    def test_feed_requires_authentication(self, api_client):
        response = api_client.get(_feed_url())
        assert response.status_code == 401


@pytest.mark.django_db
class TestFeedContent:
    def test_empty_feed_when_following_nobody(self, api_client):
        viewer = _make_user("viewer1@example.com")
        _auth(api_client, viewer)

        response = api_client.get(_feed_url())

        assert response.status_code == 200
        assert response.data["results"] == []
        assert response.data["has_next"] is False
        assert response.data["next_cursor"] is None

    def test_empty_feed_when_followed_users_have_no_updates(self, api_client):
        viewer = _make_user("viewer2@example.com")
        followed = _make_user("followed2@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        _make_project(followed)  # project exists, but no updates logged
        _auth(api_client, viewer)

        response = api_client.get(_feed_url())

        assert response.status_code == 200
        assert response.data["results"] == []

    def test_only_shows_updates_from_followed_users(self, api_client):
        viewer = _make_user("viewer3@example.com")
        followed = _make_user("followed3@example.com")
        stranger = _make_user("stranger3@example.com")
        Follow.objects.create(follower=viewer, following=followed)

        followed_project = _make_project(followed, title="Followed's project")
        stranger_project = _make_project(stranger, title="Stranger's project")
        followed_update = _make_update(
            followed_project, followed, title="From followed"
        )
        _make_update(stranger_project, stranger, title="From stranger")

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        assert response.status_code == 200
        ids = [item["id"] for item in response.data["results"]]
        assert str(followed_update.id) in ids
        assert len(ids) == 1

    def test_response_shape_has_author_project_and_photos(self, api_client):
        viewer = _make_user("viewer4@example.com")
        followed = _make_user("followed4@example.com", display_name="Alice Wanjiru")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed, title="Kilimani Towers")
        update = _make_update(
            project, followed, title="Slab poured", body="<p>Great progress</p>"
        )

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        assert response.status_code == 200
        item = response.data["results"][0]
        assert item["id"] == str(update.id)
        assert item["title"] == "Slab poured"
        assert item["entry_type"] == "milestone"
        assert item["photos"] == []
        assert item["author"]["id"] == str(followed.id)
        assert item["author"]["display_name"] == "Alice Wanjiru"
        assert "avatar_url" in item["author"]
        assert item["project"]["id"] == str(project.id)
        assert item["project"]["title"] == "Kilimani Towers"

    def test_most_recent_first(self, api_client):
        viewer = _make_user("viewer5@example.com")
        followed = _make_user("followed5@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)

        older = _make_update(project, followed, title="Older")
        newer = _make_update(project, followed, title="Newer")
        now = timezone.now()
        _set_created_at(older, now - timezone.timedelta(hours=2))
        _set_created_at(newer, now - timezone.timedelta(hours=1))

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        titles = [item["title"] for item in response.data["results"]]
        assert titles == ["Newer", "Older"]


@pytest.mark.django_db
class TestFeedVisibility:
    def test_private_project_excluded_even_if_followed(self, api_client):
        viewer = _make_user("viewer6@example.com")
        followed = _make_user("followed6@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        private_project = _make_project(
            followed, visibility=ProjectVisibility.PRIVATE, title="Private job"
        )
        _make_update(private_project, followed, title="Secret update")

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        assert response.data["results"] == []

    def test_connections_project_hidden_without_mutual_follow(self, api_client):
        viewer = _make_user("viewer7@example.com")
        followed = _make_user("followed7@example.com")
        # One-directional only: viewer follows followed, but followed
        # does not follow viewer back — not a "connection" per §1.4.1.
        Follow.objects.create(follower=viewer, following=followed)
        connections_project = _make_project(
            followed, visibility=ProjectVisibility.CONNECTIONS, title="Team only"
        )
        _make_update(connections_project, followed, title="Team update")

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        assert response.data["results"] == []

    def test_connections_project_visible_with_mutual_follow(self, api_client):
        viewer = _make_user("viewer8@example.com")
        followed = _make_user("followed8@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        Follow.objects.create(follower=followed, following=viewer)  # mutual
        connections_project = _make_project(
            followed, visibility=ProjectVisibility.CONNECTIONS, title="Team only"
        )
        update = _make_update(connections_project, followed, title="Team update")

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        ids = [item["id"] for item in response.data["results"]]
        assert str(update.id) in ids

    def test_public_project_always_visible(self, api_client):
        viewer = _make_user("viewer9@example.com")
        followed = _make_user("followed9@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        public_project = _make_project(followed, visibility=ProjectVisibility.PUBLIC)
        update = _make_update(public_project, followed)

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        ids = [item["id"] for item in response.data["results"]]
        assert str(update.id) in ids

    def test_soft_deleted_project_excluded(self, api_client):
        viewer = _make_user("viewer10@example.com")
        followed = _make_user("followed10@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)
        _make_update(project, followed)
        project.soft_delete()

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        assert response.data["results"] == []

    def test_banned_followed_users_updates_excluded(self, api_client):
        # Session 16 permission audit: the feed reuses
        # apps.projects.permissions.visible_projects_q, which now
        # excludes deactivated/banned owners — locks in that a follower
        # stops seeing a banned account's updates in their feed, even
        # though the Follow row itself still exists.
        viewer = _make_user("viewer-banned-feed@example.com")
        banned = _make_user("banned-followed@example.com", is_active=False)
        Follow.objects.create(follower=viewer, following=banned)
        project = _make_project(banned, visibility=ProjectVisibility.PUBLIC)
        _make_update(project, banned)

        _auth(api_client, viewer)
        response = api_client.get(_feed_url())

        assert response.data["results"] == []


@pytest.mark.django_db
class TestFeedCursorPagination:
    def _seed_updates(self, followed, project, count):
        now = timezone.now()
        updates = []
        for i in range(count):
            update = _make_update(project, followed, title=f"Update {i}")
            # Strictly increasing created_at, oldest first in creation
            # order — index 0 is oldest, so the feed (newest-first) will
            # return them in reverse.
            _set_created_at(update, now - timezone.timedelta(minutes=count - i))
            updates.append(update)
        return updates

    def test_pagination_covers_all_items_no_duplicates(self, api_client):
        viewer = _make_user("viewer11@example.com")
        followed = _make_user("followed11@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)
        updates = self._seed_updates(followed, project, 5)

        _auth(api_client, viewer)
        seen_ids = []
        cursor = None
        for _ in range(10):  # generous upper bound on page count
            url = _feed_url()
            response = api_client.get(
                url, {"page_size": 2, "cursor": cursor} if cursor else {"page_size": 2}
            )
            assert response.status_code == 200
            seen_ids.extend(item["id"] for item in response.data["results"])
            if not response.data["has_next"]:
                break
            cursor = response.data["next_cursor"]

        assert len(seen_ids) == len(set(seen_ids)) == 5
        assert set(seen_ids) == {str(u.id) for u in updates}

    def test_no_skip_or_duplicate_when_new_item_inserted_mid_pagination(
        self, api_client
    ):
        viewer = _make_user("viewer12@example.com")
        followed = _make_user("followed12@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)
        updates = self._seed_updates(followed, project, 4)

        _auth(api_client, viewer)

        # Page 1: fetch the first 2 (newest 2) items.
        response = api_client.get(_feed_url(), {"page_size": 2})
        assert response.status_code == 200
        page1_ids = [item["id"] for item in response.data["results"]]
        assert len(page1_ids) == 2
        cursor = response.data["next_cursor"]

        # A brand-new update is posted "at the top" of the feed, in
        # between page loads — this must not shift the already-issued
        # cursor's position and cause page 2 to skip or repeat an item.
        newest = _make_update(project, followed, title="Just posted")
        _set_created_at(newest, timezone.now() + timezone.timedelta(minutes=10))

        response = api_client.get(_feed_url(), {"page_size": 2, "cursor": cursor})
        assert response.status_code == 200
        page2_ids = [item["id"] for item in response.data["results"]]

        # The newly-inserted item must not appear on page 2 (it sorts
        # before the cursor position, i.e. it belongs on page 1, which was
        # already served) and nothing from page 1 should reappear.
        assert str(newest.id) not in page2_ids
        assert set(page1_ids).isdisjoint(page2_ids)
        assert len(page2_ids) == 2
        remaining_ids = {str(u.id) for u in updates} - set(page1_ids)
        assert set(page2_ids) == remaining_ids

    def test_invalid_cursor_falls_back_to_start_of_feed(self, api_client):
        viewer = _make_user("viewer13@example.com")
        followed = _make_user("followed13@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)
        self._seed_updates(followed, project, 3)

        _auth(api_client, viewer)
        response = api_client.get(_feed_url(), {"cursor": "not-a-real-cursor"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_cursor_page_size_is_capped(self, api_client):
        viewer = _make_user("viewer14@example.com")
        followed = _make_user("followed14@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)
        self._seed_updates(followed, project, 3)

        _auth(api_client, viewer)
        response = api_client.get(_feed_url(), {"page_size": 1})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["has_next"] is True

    def test_equal_created_at_timestamps_do_not_skip_or_duplicate(self, api_client):
        # Same created_at across multiple updates (a real possibility with
        # fast successive writes) must still page cleanly via the id
        # tiebreaker.
        viewer = _make_user("viewer15@example.com")
        followed = _make_user("followed15@example.com")
        Follow.objects.create(follower=viewer, following=followed)
        project = _make_project(followed)

        same_time = timezone.now()
        updates = [_make_update(project, followed, title=f"Tied {i}") for i in range(3)]
        for u in updates:
            _set_created_at(u, same_time)

        _auth(api_client, viewer)
        seen_ids = []
        cursor = None
        for _ in range(10):
            params = {"page_size": 1}
            if cursor:
                params["cursor"] = cursor
            response = api_client.get(_feed_url(), params)
            seen_ids.extend(item["id"] for item in response.data["results"])
            if not response.data["has_next"]:
                break
            cursor = response.data["next_cursor"]

        assert len(seen_ids) == len(set(seen_ids)) == 3
        assert set(seen_ids) == {str(u.id) for u in updates}
