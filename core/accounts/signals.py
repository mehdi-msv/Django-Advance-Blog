from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import Profile
from blog.models import Post

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def assign_post_permission_if_staff(sender, instance, created, **kwargs):
    if instance.is_staff or instance.is_superuser:
        content_type = ContentType.objects.get_for_model(Post)
        perm = Permission.objects.get(
            content_type=content_type,
            codename="add_post"
        )
        if not instance.has_perm("blog.add_post"):
            instance.user_permissions.add(perm)
