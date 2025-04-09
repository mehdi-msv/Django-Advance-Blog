from django.test import TestCase
from django.urls import reverse
from datetime import datetime

from accounts.models import User, Profile
from ..models import Post, Category

class TestBlogViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the TestBlogViews test cases. Creates a user, category,
        author profile, and a post for use in various test methods.

        - Creates a User instance with email 'mehdi' and password 'mehdi'.
        - Creates a Category instance named 'Category 1'.
        - Creates a Profile instance for the user with specific first name,
        last name, and description.
        - Creates a Post instance associated with the created author, category,
        and sets its status to True with the current date as the published date.
        """

        cls.user = User.objects.create_user(email='mehdi', password='mehdi')
        cls.category = Category.objects.create(name="Category 1")
        cls.author = Profile.objects.create(
            user=cls.user,
            first_name="test_first_name",
            last_name="test_last_name",
            description="A description",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            title="A title",
            content="Some content",
            category=cls.category,
            status=True,
            published_date=datetime.now(),
        )

    def test_blog_index_successful_response(self):
                        
        url = reverse("blog:index")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "mehdi")
        self.assertTrue(str(response.content).find("mehdi") > -1)
        self.assertIn("mehdi", response.content.decode())
        self.assertTrue("mehdi" in response.content.decode())

    def test_blog_post_detail_logged_in_response(self):
        
        self.client.force_login(self.user)
        url = reverse("blog:post-detail", args=[self.post.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_blog_post_detail_anonymous_response(self):
        # self.client.logout() ## when we use (self.client.force_login(self.user)) in setup(self)
        # self.client = Client()
        
        url = reverse("blog:post-detail", args=[self.post.id])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
