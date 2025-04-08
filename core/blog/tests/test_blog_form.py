from django.test import TestCase
from datetime import datetime
from ..forms import PostForm
from ..models import Category

class TestPostForm(TestCase):
    def test_form_has_fields(self):
        """
        Test that the PostForm contains the expected fields.
        Verifies that the form fields match the expected list of
        fields: 'title', 'content', 'category', 'status', 'published_date'.
        """
        form = PostForm()
        expected = ['title', 'content', 'category', 'status', 'published_date']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
    def test_post_form_with_valid_data_is_valid(self):
        """
        Verifies that a PostForm with valid data is valid.
        Given a category object and a dictionary of valid form data,
        creates a PostForm and verifies that it is valid.
        """
        category_obj = Category.objects.create(name='Category 1')
        form_data = {
            'title': 'A title',
            'content': 'Some content',
            'category': category_obj,
            'status': True,
            'published_date': datetime.now(),
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
    def test_post_form_with_invalid_data_is_not_valid(self):
        """
        Verifies that a PostForm with no data is not valid.
        Given no data, creates a PostForm and verifies that it is not valid.
        """
        form = PostForm(data={})
        self.assertFalse(form.is_valid())
