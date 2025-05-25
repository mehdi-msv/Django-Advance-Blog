from django.contrib.auth import get_user_model
from mail_templated import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Profile


User = get_user_model()


@shared_task
def send_verification_email(user_id):
    """
    Send verification email to the user with the given user_id.

    If the user does not exist, do nothing.
    """
    try:
        # Get the user object
        user = User.objects.get(id=user_id)
        # Generate a JWT token for the user
        token = str(RefreshToken.for_user(user).access_token)
        # Create an email message
        message = EmailMessage(
            "email/email-confirm.tpl",
            {"user": user, "token": token},
            "mehdi.hunter.3242@gmail.com",
            # Send the email to the user's email address
            to=[user.email],
        )
        # Send the email
        message.send()
    except User.DoesNotExist:
        # If the user does not exist, do nothing
        pass

@shared_task
def monthly_add_score():
    """
    Adds monthly score to verified users who haven't had their score updated in the last month.
    """
    now = timezone.now()
    one_month = timedelta(days=30)

    profiles = Profile.objects.filter(
        user__created_date__lte=now - one_month,
        last_score_update__lte=now - one_month,
        user__is_verified=True,
        score__lt=100
    ).select_related('user')

    for profile in profiles:
        profile.score = min(profile.score + 10, 100)
        profile.last_score_update = now
        profile.save()
