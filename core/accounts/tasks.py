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
    Send verification email to the user with the given user_id using JWT token
    with a custom claim (purpose=email_verification) and short expiration time.
    """
    try:
        user = User.objects.get(id=user_id)

        # Create a refresh token and access token
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add a custom claim to clarify the purpose of the token
        access_token['purpose'] = 'email_verification'

        # Set token expiration to 1 day for email verification
        access_token.set_exp(lifetime=timedelta(days=1))

        # Convert token to string
        token = str(access_token)

        # Prepare and send the email
        message = EmailMessage(
            "email/email-confirm.tpl",
            {"user": user, "token": token},
            "mehdi.hunter.3242@gmail.com",
            to=[user.email],
        )
        message.send()
    except User.DoesNotExist:
        # If user not found, silently ignore
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
