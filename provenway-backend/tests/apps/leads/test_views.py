import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.leads.models import InterestSignup


@pytest.fixture
def api_client():
    return APIClient()


def _payload(**overrides):
    payload = {
        "name": "Jane Developer",
        "email": "jane@example.com",
        "organization_name": "Acme Construction",
        "interest_type": "construction_firm",
        "message": "We'd like to hear more.",
        "source_page": "for-construction-firms",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
class TestInterestSignupEndpoint:
    def test_valid_submission_creates_row(self, api_client):
        response = api_client.post(reverse("leads:interest-create"), _payload())
        assert response.status_code == 201
        assert InterestSignup.objects.filter(email="jane@example.com").exists()

    def test_missing_required_field_returns_400(self, api_client):
        payload = _payload()
        del payload["name"]
        response = api_client.post(reverse("leads:interest-create"), payload)
        assert response.status_code == 400
        assert not InterestSignup.objects.filter(email="jane@example.com").exists()

    def test_invalid_email_returns_400(self, api_client):
        response = api_client.post(reverse("leads:interest-create"), _payload(email="not-an-email"))
        assert response.status_code == 400

    def test_invalid_interest_type_returns_400(self, api_client):
        response = api_client.post(reverse("leads:interest-create"), _payload(interest_type="bogus"))
        assert response.status_code == 400

    def test_honeypot_filled_returns_201_without_saving(self, api_client):
        response = api_client.post(
            reverse("leads:interest-create"), _payload(email="bot@example.com", website="http://spam.example")
        )
        assert response.status_code == 201
        assert not InterestSignup.objects.filter(email="bot@example.com").exists()

    def test_rate_limit_blocks_after_five_requests_per_minute(self, api_client):
        from django.core.cache import cache
        from django.test import override_settings

        cache.clear()
        with override_settings(RATELIMIT_ENABLE=True):
            last_response = None
            for i in range(6):  # limit is 5/m
                last_response = api_client.post(
                    reverse("leads:interest-create"), _payload(email=f"ratelimit{i}@example.com")
                )
            assert last_response.status_code == 429
        cache.clear()
