from mail_templated import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from celery import shared_task


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
