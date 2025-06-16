"""
Advanced test suite for the accounts app API endpoints (profile).
"""
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_profile_authenticated(authenticated_client):
    """
    Test the profile endpoint returns 200 for authenticated user.
    """
    url = reverse("accounts:api-v1:profile")
    response = authenticated_client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_profile_unauthenticated(api_client):
    """
    Test the profile endpoint returns 401 for unauthenticated user.
    """
    url = reverse("accounts:api-v1:profile")
    response = api_client.get(url)
    assert response.status_code == 401

