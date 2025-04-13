import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import datetime

from accounts.models import User
from ..models import Post


@pytest.fixture
def api_client():
    
    """
    A fixture that provides an instance of APIClient for making API requests.

    Returns:
        APIClient: An instance of Django's APIClient for testing.
    """

    return APIClient()


@pytest.fixture
def test_user():
    """
    A fixture that creates and returns a test user instance for database operations.

    This fixture is used in tests where a user object is required. The user is created
    with the email "test@example.com", the password "testpassword123", and is marked as staff.

    Returns:
        User: An instance of the User model with predefined attributes.
    """

    return User.objects.create_user(
        email="test@example.com",
        password="testpassword123",
        is_staff=True,
        is_verified=True
    )


@pytest.mark.django_db
class TestPostAPI:
    def test_post_list_api(self, api_client):
        """
        Test the API endpoint for retrieving a list of posts.

        This test sends a GET request to the post list endpoint and verifies that the
        response status code is HTTP 200 OK, indicating a successful retrieval of the
        post list.
        """

        url = reverse("blog:api-v1:post-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_create_post_response_201(self, api_client, test_user):
        """
        Test the API endpoint for creating a new post.

        This test authenticates a test user, sends a POST request to the post list
        endpoint with valid post data, and verifies that a new post is successfully
        created. It checks that the response status code is HTTP 201 CREATED and
        that the post count increases by one.
        """

        api_client.force_authenticate(user=test_user)
        url = reverse("blog:api-v1:post-list")
        data = {
            "title": "Test Post",
            "content": "Description",
            "status": True,
            "published_date": datetime.now()
        }
        post_count_before = Post.objects.count()
        response = api_client.post(url, data)
        post_count_after = Post.objects.count()
        assert post_count_after == post_count_before + 1
        assert response.status_code == 201
        
    def test_create_post_response_401(self, api_client):
        """
        Test that an unauthorized user can't create a post.

        This test sends a POST request to the post list endpoint with a valid data
        payload, but without authenticating as a user. The response status code is
        expected to be HTTP 401 Unauthorized, indicating that the user is not
        authenticated and cannot create a post.
        """
        
        url = reverse("blog:api-v1:post-list")
        data = {
            "title": "Test Post",
            "content": "Description",
            "status": True,
            "published_date": datetime.now()
        }
        response = api_client.post(url, data)
        assert response.status_code == 401
        
    def test_create_post_invalid_data_response_400_status(
        self, api_client, test_user
    ):
        """
        Test the API endpoint for creating a new post with invalid data.

        This test authenticates a user, sends a POST request to the post list
        endpoint with invalid post data, and verifies that the response status
        code is HTTP 400 Bad Request, indicating that the post was not created.
        """
        url = reverse("blog:api-v1:post-list")
        data = {"title": "test", "content": "description"}
        user = test_user

        api_client.force_authenticate(user=user)
        response = api_client.post(url, data)
        assert response.status_code == 400
