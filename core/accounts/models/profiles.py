from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .users import User

class Profile(models.Model):
    """
    Custom Profile Model for Accounts app
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    score = models.PositiveIntegerField(default=50)
    last_score_update = models.DateTimeField(default=timezone.now)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
    def can_post_directly(self):
        return self.score >= 20
    
    def decrease_score(self, amount):
        self.score = max(0, self.score - amount)
        self.last_score_update = timezone.now()
        self.save()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
