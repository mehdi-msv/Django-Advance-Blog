from django.urls import path, include
from .views import (
    ProfileDetailView,
    CustomLoginView,
    SignUpView,
    VerifyAccountTokenView,
    SendVerificationEmailView,
    PasswordResetConfirmView,
    CustomPasswordChangeView,
    CustomPasswordResetView,
    CustomLogoutView,
)


app_name = "accounts"


urlpatterns = [
    path("api/v1/", include("accounts.api.v1.urls")),
    path("api/v2/", include("djoser.urls")),
    path("api/v2/", include("djoser.urls.jwt")),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify/<str:token>/", VerifyAccountTokenView.as_view(), name="verify"),
    path("send-verification-email/", SendVerificationEmailView.as_view(), name="send-verification-email"),
    path("change-password/", CustomPasswordChangeView.as_view(), name="change-password"),
    path("reset-password/", CustomPasswordResetView.as_view(), name="reset-password"),
    path("reset-password/<str:token>/", PasswordResetConfirmView.as_view(), name="reset-password-confirm"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
