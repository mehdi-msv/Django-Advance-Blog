"""
Shared fixtures for accounts app tests.
"""

import pytest
from accounts.models import User, Profile
from rest_framework.test import APIClient


@pytest.fixture
def user_data():
    """
    Returns a dictionary of valid user data.
    """
    return {"email": "testuser@accounts.com", "password": "testpass123"}


@pytest.fixture
def test_user(db, user_data):
    """
    Creates and returns a test user and profile.
    """
    user = User.objects.create_user(**user_data)
    profile = Profile.objects.get(user=user)
    return user, profile


@pytest.fixture
def api_client():
    """
    Returns a DRF APIClient instance.
    """
    return APIClient()


@pytest.fixture
def authenticated_client(test_user, api_client, user_data):
    """
    Returns an authenticated APIClient for the test user.
    """
    user, _ = test_user
    api_client.force_authenticate(user=user)
    return api_client
