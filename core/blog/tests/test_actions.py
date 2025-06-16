"""
Advanced action tests for the blog app.
"""
import pytest

@pytest.mark.django_db
def test_post_decrease_score_action(test_post, test_user):
    """
    Test the decrease_score method on the post's author profile as an action.
    """
    user, profile = test_user
    post = test_post
    old_score = profile.score
    profile.decrease_score(10)
    profile.refresh_from_db()
    assert profile.score == old_score - 10
