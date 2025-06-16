"""
Advanced test suite for the custom User and Profile models in the accounts app.
"""

import pytest


@pytest.mark.django_db
def test_create_user_and_profile(test_user):
    """
    Test user and profile creation and default values.
    """
    user, profile = test_user
    assert user.email
    assert profile.user == user
    assert profile.score == 50
    assert profile.full_name() == user.email


@pytest.mark.django_db
def test_profile_full_name(test_user):
    """
    Test full_name method returns correct value.
    """
    user, profile = test_user
    profile.first_name = "Mehdi"
    profile.last_name = "Msv"
    profile.save()
    assert profile.full_name() == "Mehdi Msv"


@pytest.mark.django_db
def test_profile_score_methods(test_user):
    """
    Test can_post_directly and decrease_score methods.
    """
    user, profile = test_user
    assert profile.can_post_directly() is True
    profile.decrease_score(40)
    assert profile.score == 10
    assert profile.can_post_directly() is False
