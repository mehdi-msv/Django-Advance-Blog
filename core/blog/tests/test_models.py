"""
Advanced test suite for the Post and Category models in the blog app.
"""

import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_create_category(test_category):
    """
    Test creating a new category instance using the shared fixture.
    """
    assert test_category.name == "Test Category"


@pytest.mark.django_db
def test_create_post(test_post, test_user, test_category):
    """
    Test creating a new post instance using shared fixtures.
    """
    user, profile = test_user
    post = test_post
    assert post.title == "Test Post"
    assert post.author == profile
    assert post.category == test_category
    assert post.status is True
    assert post.published_date <= timezone.now()


@pytest.mark.django_db
def test_post_snippet(test_post):
    """
    Test the get_snippet method of Post model.
    """
    snippet = test_post.get_snippet()
    assert isinstance(snippet, str)
    assert snippet
