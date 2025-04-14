from django.core.management.base import BaseCommand
import random
from faker import Faker
from datetime import datetime

from blog.models import Post, Category
from accounts.models import User, Profile


categories = ["Python", "Django", "JavaScript", "React", "Node.js"]


class Command(BaseCommand):
    help = "Inserts random data into the database"
    """
    Initializes the command with a Faker instance to generate fake data.
    """

    def __init__(self):
        """
        Initializes the Command class.

        This constructor initializes the parent class and sets up an instance of the
        Faker library used to generate fake data for populating the database.
        """
        super().__init__()
        self.faker = Faker()

    def handle(self, *args, **options):
        """
        Handles the command to insert random data into the database.

        This function creates a fake user account, creates a profile for that user,
        creates categories for the blog posts, and creates three fake blog posts
        associated with the user and categories.

        Args:
            *args: A list of positional arguments.
            **options: A dictionary of keyword arguments.

        Returns:
            None
        """
        user = User.objects.create_user(
            email=self.faker.email(),
            password="@/12345a",
        )
        profile = Profile.objects.get(user=user)
        # Set the user's first and last name
        profile.first_name = self.faker.first_name()
        profile.last_name = self.faker.last_name()
        profile.description = self.faker.text()
        profile.save()

        # Create categories for the blog posts
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)

        # Create three fake blog posts associated with the user and categories
        for _ in range(3):
            Post.objects.create(
                author=profile,
                title=self.faker.sentence(),
                content=self.faker.text(),
                category=random.choice(Category.objects.all()),
                status=random.choice([True, False]),
                published_date=datetime.now(),
            )
        self.stdout.write(self.style.SUCCESS("✅ Fake data inserted successfully!"))
