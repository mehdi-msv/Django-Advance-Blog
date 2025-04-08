from django.test import TestCase
from django.urls import reverse, resolve
from .views import IndexView
# Create your tests here.

class TestUrl(TestCase):

    def test_url_exists_at_correct_location(self):
        url = reverse("blog:index")
        self.assertEquals(resolve(url).func.view_class, IndexView)
        
        