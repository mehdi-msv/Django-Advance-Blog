from django.urls import path, include
from .views import (
    ProfileDetailView,
    CustomLoginView,
    SignUpView,
    VerifyAccountTokenView,
    SendVerificationEmailView
)


app_name = "accounts"


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("api/v1/", include("accounts.api.v1.urls")),
    path("api/v2/", include("djoser.urls")),
    path("api/v2/", include("djoser.urls.jwt")),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("signin/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify/<str:token>/", VerifyAccountTokenView.as_view(), name="verify"),
    path("send-verification-email/", SendVerificationEmailView.as_view(), name="send-verification-email"),
]
