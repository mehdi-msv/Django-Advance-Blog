"""
Advanced integration tests for the blog app.
"""

import pytest


@pytest.mark.django_db
def test_user_and_post_integration(test_user, test_post):
    """
    Integration test to ensure user and post creation work together.
    """
    user, profile = test_user
    post = test_post
    assert post.author == profile
    assert user.email in post.author.user.email
