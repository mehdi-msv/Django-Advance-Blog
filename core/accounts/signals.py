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
    """
    Automatically create a Profile for every new user.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def assign_post_permission_if_staff(sender, instance, **kwargs):
    """
    Assign the 'add_post' permission to staff or superusers automatically.
    Ensures the user has the required permission for creating blog posts.
    """
    if instance.is_staff or instance.is_superuser:
        content_type = ContentType.objects.get_for_model(Post)
        permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename="add_post",
            defaults={"name": "Can add post"},
        )
        if not instance.has_perm("blog.add_post"):
            instance.user_permissions.add(permission)
