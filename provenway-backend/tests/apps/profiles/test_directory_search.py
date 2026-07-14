import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.authentication.models import Discipline
from apps.authentication.models import User
from apps.profiles.models import Profile


@pytest.fixture
def api_client():
    return APIClient()


def _make_user(email, **kwargs):
    kwargs.setdefault("display_name", "Test User")
    kwargs.setdefault("is_email_verified", True)
    return User.objects.create_user(email=email, password="StrongPass1", **kwargs)


def _set_profile(user, **kwargs):
    """Fetch the auto-created Profile for `user`, set fields, and save —
    deliberately uses .save() (not .update()) so the post_save signal
    that maintains search_vector actually fires, the same as it would for
    a real PATCH /profiles/me/ request.
    """
    profile = Profile.objects.get(user=user)
    for field, value in kwargs.items():
        setattr(profile, field, value)
    profile.save()
    return profile


def _search(api_client, **params):
    url = reverse("directory:search")
    return api_client.get(url, params)


@pytest.mark.django_db
class TestDirectorySearchTextMatch:
    def test_matches_on_display_name(self, api_client):
        user = _make_user("amara@example.com", display_name="Amara Njoroge")
        _set_profile(user)

        response = _search(api_client, q="Njoroge")

        assert response.status_code == 200
        ids = [row["id"] for row in response.data["results"]]
        assert str(user.id) in ids

    def test_matches_on_headline(self, api_client):
        user = _make_user(
            "kip@example.com", headline="Structural engineer for high-rises"
        )
        _set_profile(user)

        response = _search(api_client, q="high-rises")

        ids = [row["id"] for row in response.data["results"]]
        assert str(user.id) in ids

    def test_matches_on_bio(self, api_client):
        user = _make_user("wanjiru@example.com")
        _set_profile(user, bio="Specialises in earthquake-resistant foundations.")

        response = _search(api_client, q="earthquake-resistant")

        ids = [row["id"] for row in response.data["results"]]
        assert str(user.id) in ids

    def test_matches_on_firm_name(self, api_client):
        user = _make_user("otieno@example.com")
        _set_profile(user, firm_name="Cilneod Kenya Contractors")

        response = _search(api_client, q="Cilneod")

        ids = [row["id"] for row in response.data["results"]]
        assert str(user.id) in ids

    def test_no_match_returns_empty(self, api_client):
        user = _make_user("nobody@example.com", display_name="Someone Else")
        _set_profile(user)

        response = _search(api_client, q="xyznonexistentquery")

        assert response.data["results"] == []


@pytest.mark.django_db
class TestDirectorySearchDisciplineFilter:
    def test_filters_by_single_discipline(self, api_client):
        architect = _make_user("architect@example.com")
        _set_profile(architect, disciplines=[Discipline.ARCHITECT])

        contractor = _make_user("contractor@example.com")
        _set_profile(contractor, disciplines=[Discipline.CONTRACTOR])

        response = _search(api_client, discipline=Discipline.ARCHITECT)

        ids = [row["id"] for row in response.data["results"]]
        assert str(architect.id) in ids
        assert str(contractor.id) not in ids

    def test_filters_by_comma_separated_disciplines(self, api_client):
        architect = _make_user("architect2@example.com")
        _set_profile(architect, disciplines=[Discipline.ARCHITECT])

        qs = _make_user("qs@example.com")
        _set_profile(qs, disciplines=[Discipline.QS])

        contractor = _make_user("contractor2@example.com")
        _set_profile(contractor, disciplines=[Discipline.CONTRACTOR])

        response = _search(
            api_client, discipline=f"{Discipline.ARCHITECT},{Discipline.QS}"
        )

        ids = {row["id"] for row in response.data["results"]}
        assert str(architect.id) in ids
        assert str(qs.id) in ids
        assert str(contractor.id) not in ids

    def test_invalid_discipline_returns_400(self, api_client):
        response = _search(api_client, discipline="not_a_real_discipline")
        assert response.status_code == 400


@pytest.mark.django_db
class TestDirectorySearchVerifiedFilter:
    def test_filters_verified_true(self, api_client):
        verified = _make_user("verified@example.com", is_verified=True)
        _set_profile(verified)

        unverified = _make_user("unverified@example.com", is_verified=False)
        _set_profile(unverified)

        response = _search(api_client, verified="true")

        ids = [row["id"] for row in response.data["results"]]
        assert str(verified.id) in ids
        assert str(unverified.id) not in ids

    def test_invalid_verified_value_returns_400(self, api_client):
        response = _search(api_client, verified="maybe")
        assert response.status_code == 400


@pytest.mark.django_db
class TestDirectorySearchRadius:
    def test_radius_search_returns_only_users_within_range(self, api_client):
        # Nairobi CBD
        nearby = _make_user("nearby@example.com")
        _set_profile(nearby, location_lat="-1.286389", location_lng="36.817223")

        # Mombasa — ~440km from Nairobi, well outside a 50km radius
        far = _make_user("far@example.com")
        _set_profile(far, location_lat="-4.043477", location_lng="39.658871")

        # No location set at all
        no_location = _make_user("nolocation@example.com")
        _set_profile(no_location)

        response = _search(api_client, lat="-1.286389", lng="36.817223", radius_km="50")

        assert response.status_code == 200
        ids = [row["id"] for row in response.data["results"]]
        assert str(nearby.id) in ids
        assert str(far.id) not in ids
        assert str(no_location.id) not in ids

    def test_partial_geo_params_returns_400(self, api_client):
        response = _search(api_client, lat="-1.28", lng="36.81")
        assert response.status_code == 400

    def test_location_text_filter(self, api_client):
        user = _make_user("nairobiuser@example.com")
        _set_profile(user, location_text="Westlands, Nairobi")

        other = _make_user("mombasauser@example.com")
        _set_profile(other, location_text="Nyali, Mombasa")

        response = _search(api_client, location="Nairobi")

        ids = [row["id"] for row in response.data["results"]]
        assert str(user.id) in ids
        assert str(other.id) not in ids


@pytest.mark.django_db
class TestDirectorySearchExcludesInactiveUsers:
    def test_inactive_user_never_appears(self, api_client):
        active = _make_user("active@example.com", display_name="Active Person")
        _set_profile(active)

        inactive = _make_user(
            "inactive@example.com", display_name="Deactivated Person", is_active=False
        )
        _set_profile(inactive)

        response = _search(api_client)

        ids = [row["id"] for row in response.data["results"]]
        assert str(active.id) in ids
        assert str(inactive.id) not in ids

    def test_inactive_user_excluded_even_when_matching_query(self, api_client):
        inactive = _make_user(
            "banned@example.com", display_name="Banned Contractor", is_active=False
        )
        _set_profile(inactive)

        response = _search(api_client, q="Banned")

        ids = [row["id"] for row in response.data["results"]]
        assert str(inactive.id) not in ids


@pytest.mark.django_db
class TestDirectorySearchResponseShape:
    def test_response_includes_expected_fields(self, api_client):
        user = _make_user(
            "shape@example.com",
            display_name="Shape Test",
            headline="Quantity Surveyor",
            is_verified=True,
        )
        _set_profile(
            user,
            location_text="Kilimani, Nairobi",
            firm_name="Test Firm",
            disciplines=[Discipline.QS],
        )

        response = _search(api_client, q="Shape")

        row = next(r for r in response.data["results"] if r["id"] == str(user.id))
        assert row["display_name"] == "Shape Test"
        assert row["headline"] == "Quantity Surveyor"
        assert row["is_verified"] is True
        assert row["location_text"] == "Kilimani, Nairobi"
        assert row["firm_name"] == "Test Firm"
        assert row["disciplines"] == [Discipline.QS]

    def test_search_works_without_authentication(self, api_client):
        user = _make_user("anon@example.com", display_name="Anon Visible")
        _set_profile(user)

        response = _search(api_client, q="Anon")

        assert response.status_code == 200
