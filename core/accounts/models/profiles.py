from django.db import models
from django.utils import timezone
from .users import User


class Profile(models.Model):
    """
    Custom Profile Model for Accounts app
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    image = models.ImageField(
        upload_to="profile_images/",
        default="defaults/default_profile.png",
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True, null=True)
    score = models.PositiveIntegerField(default=50)
    last_score_update = models.DateTimeField(default=timezone.now)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def can_post_directly(self):
        return self.score >= 20

    def decrease_score(self, amount):
        self.score = max(0, self.score - amount)
        self.last_score_update = timezone.now()
        self.save()

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email

    def __str__(self):
        return self.user.email
