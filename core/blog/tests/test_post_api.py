import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestPostAPI:
    def test_post_list_api(self, client):
        # client = APIClient() no need
        url = reverse("blog:api-v1:post-list")
        response = client.get(url)
        print(response)
        assert response.status_code == status.HTTP_200_OK
