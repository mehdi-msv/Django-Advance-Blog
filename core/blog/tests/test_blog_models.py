from django.test import TestCase
from datetime import datetime

from ..models import Post, Category
from accounts.models import Profile, User

# Create your tests here.
class TestPostModel(TestCase):
    def setUp(self):
        """
        Sets up test data for Post model tests.

        This method creates and saves a Category object, a User object,
        and a Profile object to be used as test data in the Post model tests.
        """
        self.category_obj = Category.objects.create(name="Category 1")
        self.user = User.objects.create_user(email="testuser@example.com", password="testpassword")
        self.author_obj = Profile.objects.create(
            user=self.user,
            first_name="test_first_name",
            last_name="test_last_name",
            description="A description",
        )

    def test_create_post_with_valid_data(self):
        """
        Test the creation of a Post instance with valid data.

        This test verifies that a Post object can be successfully created
        with valid attributes and checks if the object exists in the database.
        """
        # Create a Post object with valid data
        post_obj = Post.objects.create(
            author=self.author_obj,
            title="A title",
            content="Some content",
            category=self.category_obj,
            status=True,
            published_date=datetime.now(),
        )

        # Check that the Post object exists in the database
        self.assertTrue(Post.objects.filter(pk=post_obj.pk).exists())

        # Verify that the title of the Post object is correct
        self.assertEquals(post_obj.title, "A title")

    def test_create_post_with_invalid_data(self):
        """
        Test the creation of a Post instance with invalid data.

        This test verifies that a Post object raises a ValueError
        when invalid attributes are provided.
        """
        with self.assertRaises(ValueError):
            Post.objects.create(
                # author is of type str instead of Profile
                author='heo',
                title="",
                content="",
                category=self.category_obj,
                status=True,
                published_date=datetime.now(),
            )
            
