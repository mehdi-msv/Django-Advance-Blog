"""
Advanced test suite for the PostViewSet in the blog app.
"""
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_post_list_authenticated(authenticated_client):
    """
    Test the post list endpoint returns 200 for authenticated user.
    """
    url = reverse("blog:post-list")
    response = authenticated_client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_post_list_unauthenticated(api_client):
    """
    Test the post list endpoint returns 200 for unauthenticated user (public access).
    """
    url = reverse("blog:api-v1:post-list")
    response = api_client.get(url)
    assert response.status_code == 200
