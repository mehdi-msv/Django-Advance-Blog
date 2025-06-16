"""
Shared fixtures for blog app tests.
"""
import pytest
from accounts.models import User, Profile
from blog.models import Category, Post
from rest_framework.test import APIClient
from django.utils import timezone

@pytest.fixture
def user_data():
    """
    Returns a dictionary of valid user data.
    """
    return {"email": "testuser@blog.com", "password": "testpass123"}

@pytest.fixture
def test_user(db, user_data):
    """
    Creates and returns a test user and profile.
    """
    user = User.objects.create_user(**user_data)
    profile = Profile.objects.get(user=user)
    return user, profile

@pytest.fixture
def test_category(db):
    """
    Creates and returns a test category.
    """
    return Category.objects.create(name="Test Category")

@pytest.fixture
def test_post(db, test_user, test_category):
    """
    Creates and returns a test post.
    """
    user, profile = test_user
    return Post.objects.create(
        author=profile,
        title="Test Post",
        content="Test content",
        category=test_category,
        status=True,
        published_date=timezone.now(),
    )

@pytest.fixture
def api_client():
    """
    Returns a DRF APIClient instance.
    """
    return APIClient()

@pytest.fixture
def authenticated_client(test_user, api_client):
    """
    Returns an authenticated APIClient for the test user.
    """
    user, _ = test_user
    api_client.force_authenticate(user=user)
    return api_client
