"""
Advanced test suite for the Post serializer in the blog app.
"""
import pytest
from blog.api.v1.serializers import PostSerializer
from django.utils import timezone

@pytest.mark.django_db
def test_post_serializer_valid(test_user, test_category, rf):
    """
    Test that the PostSerializer validates correct data using shared fixtures and correct fields.
    """
    user, profile = test_user
    data = {
        "title": "Test Post",
        "content": "Test content",
        "category_id": test_category.id,
        "status": True,
        "published_date": timezone.now(),
    }
    request = rf.post("/fake-url/")
    request.user = user
    serializer = PostSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), serializer.errors

@pytest.mark.django_db
def test_post_serializer_invalid():
    """
    Test that the PostSerializer does not validate empty data.
    """
    serializer = PostSerializer(data={})
    assert not serializer.is_valid()

@pytest.mark.django_db
def test_post_serializer_missing_fields(test_user):
    """
    Test that the PostSerializer does not validate data with missing required fields.
    """
    user, profile = test_user
    data = {
        "author": profile.id,
        "title": "",
        "content": "",
        "category": None,
        "status": True,
        "published_date": None,
    }
    serializer = PostSerializer(data=data)
    assert not serializer.is_valid()
