from django.contrib.auth import get_user_model
from mail_templated import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.utils.module_loading import import_string

from .utils import SCOPE_CONFIG_MAP
from .models import Profile
from .models.throttle_records import ThrottleRecord
from core.settings.base import EMAIL_HOST_USER

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
        access_token["purpose"] = "email_verification"

        # Set token expiration to 1 day for email verification
        access_token.set_exp(lifetime=timedelta(days=1))

        # Convert token to string
        token = str(access_token)

        # Prepare and send the email
        message = EmailMessage(
            "email/email-confirm.tpl",
            {"user": user, "token": token},
            EMAIL_HOST_USER,
            to=[user.email],
        )
        message.send()
    except User.DoesNotExist:
        # If user not found, silently ignore
        pass


@shared_task
def send_password_reset_email(user_id):
    """
    Send password reset email to the user with the given user_id using JWT token
    with a custom claim (purpose=password_reset) and short expiration time.
    """
    try:
        user = User.objects.get(id=user_id)

        # Create a refresh token and access token
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Add a custom claim to clarify the purpose of the token
        access_token["purpose"] = "password_reset"

        # Set token expiration to 10 minutes for email verification
        access_token.set_exp(lifetime=timedelta(minutes=10))

        # Convert token to string
        token = str(access_token)

        # Prepare and send the email
        message = EmailMessage(
            "email/email-password-reset.tpl",
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
        score__lt=100,
    ).select_related("user")

    for profile in profiles:
        profile.score = min(profile.score + 10, 100)
        profile.last_score_update = now
        profile.save()


@shared_task
def clear_throttle_after_grace():
    """
    Periodic task that deletes throttle records of users who haven't
    violated throttling rules for twice their cooldown period.

    Cooldown = base_window * 2^level
    base_window is fetched per-scope from throttle class or view class.
    Only records with `last_blocked_at` are considered.
    """
    now = timezone.now()
    records = ThrottleRecord.objects.exclude(last_blocked_at__isnull=True)

    for record in records:
        scope_config = SCOPE_CONFIG_MAP.get(record.scope)
        if not scope_config:
            continue  # Unknown scope

        # If config is a string, import the class
        if isinstance(scope_config, str):
            try:
                scope_config = import_string(scope_config)
            except ImportError:
                continue  # Invalid path, skip

        # Try to get base_window from class attribute
        base_window = getattr(
            scope_config, "throttle_base_window", None
        ) or getattr(scope_config, "base_window", None)
        if base_window is None:
            continue  # Skip if not defined

        cooldown = base_window * (2**record.level)
        grace_period = timedelta(seconds=cooldown * 2)

        if record.last_blocked_at + grace_period < now:
            record.delete()
