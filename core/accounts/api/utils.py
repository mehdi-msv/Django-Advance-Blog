import threading
from mail_templated import EmailMessage
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class EmailVerificationThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        user = get_object_or_404(User, email=self.email)
        token = str(RefreshToken.for_user(user).access_token)
        message = EmailMessage(
            'email/email-confirm.tpl',
            {'user': self.email, 'token': token},
            'mehdi.hunter.3242@gmail.com',
            to=[self.email]
        )
        message.send()
# class EmailThread(threading.Thread):
#   # overriding constructor
#   def __init__(self, message):
#     # calling parent class constructor
#     threading.Thread.__init__(self)
#     self.message = message
#   def run(self):
#     self.message.send()