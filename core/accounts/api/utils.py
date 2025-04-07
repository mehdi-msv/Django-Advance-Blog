import threading
from mail_templated import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken


class EmailVerificationThread(threading.Thread):
    def __init__(self, user):
        self.user = user
        threading.Thread.__init__(self)

    def run(self):
        user = self.user
        token = str(RefreshToken.for_user(user).access_token)
        message = EmailMessage(
            "email/email-confirm.tpl",
            {"user": user, "token": token},
            "mehdi.hunter.3242@gmail.com",
            to=[user],
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
