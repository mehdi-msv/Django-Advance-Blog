"""
Advanced test suite for custom permissions in the blog app.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["put", "patch"])
def test_owner_can_patch_post_title(
    authenticated_client, test_user, test_post, method
):
    """
    Ensure that the owner can successfully perform a partial update (PATCH)
    to modify only the title of their own post.
    """
    user, _ = test_user
    post = test_post
    url = reverse("blog:api-v1:post-detail", kwargs={"slug": post.slug})
    # Owner reads their own post
    response = authenticated_client.get(url)
    assert response.status_code == 200

    updated_data = {
        "title": f"Updated via {method.upper()}",
        "category_id": post.category.id,
        "content": "Updated content",
        "status": True,
        "published_date": post.published_date.isoformat(),
    }
    if method == "patch":
        updated_data = {
            "title": f"Updated via {method.upper()}",
            "category_id": post.category.id,
        }
    # Owner updates the title
    response = getattr(authenticated_client, method)(
        url, data=updated_data, format="json"
    )

    assert response.status_code == 200
    post.refresh_from_db()
    assert response.data["title"] == updated_data["title"]


@pytest.mark.django_db
def test_non_owner_can_read_but_cannot_update(
    api_client, test_post, django_user_model
):
    """
    Non-owner should be able to read the post (GET), but not update it (PATCH).
    """
    # Create a different user
    other_user = django_user_model.objects.create_user(
        email="other@blog.com", password="testpass123"
    )
    api_client.force_authenticate(user=other_user)
    post = test_post
    url = reverse("blog:api-v1:post-detail", kwargs={"slug": post.slug})
    # Non-owner tries to read the post
    response = api_client.get(url)
    assert response.status_code == 200

    updated_title = post.title + " Updated"

    # Non-owner tries to update the post
    response = api_client.patch(
        url, {"title": updated_title}, content_type="application/json"
    )

    assert response.status_code == 404
