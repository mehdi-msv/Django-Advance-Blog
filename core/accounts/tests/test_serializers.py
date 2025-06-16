"""
Advanced test suite for the User serializer in the accounts app.
"""

import pytest
from accounts.api.v1.serializers import RegistrationSerializer


@pytest.mark.django_db
def test_registration_serializer_valid(user_data):
    """
    Test that the RegistrationSerializer validates correct data.
    """
    data = user_data.copy()
    data["password1"] = data["password"]
    serializer = RegistrationSerializer(data=data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_registration_serializer_invalid():
    """
    Test that the RegistrationSerializer does not validate empty data.
    """
    serializer = RegistrationSerializer(data={})
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_registration_serializer_duplicate_email(test_user, user_data):
    """
    Test that the RegistrationSerializer does not allow duplicate emails.
    """
    data = user_data.copy()
    data["password1"] = data["password"]
    serializer = RegistrationSerializer(data=data)
    assert not serializer.is_valid() or "email" in serializer.errors
