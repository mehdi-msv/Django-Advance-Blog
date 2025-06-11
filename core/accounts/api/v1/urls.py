from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# from rest_framework.authtoken.views import ObtainAuthToken

app_name = "api-v1"


urlpatterns = [
    path(
        "registration/",
        views.RegistrationAPIView.as_view(),
        name="registration",
    ),
    path(
        "token/login/",
        views.CustomObtainAuthToken.as_view(),
        name="token-login",
    ),
    path(
        "token/logout/", views.DiscardAuthToken.as_view(), name="token-logout"
    ),
    path(
        "jwt/create/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "change-password",
        views.ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path("profile/", views.ProfileAPIView.as_view(), name="profile"),
    path(
        "email-verification/confirm/<str:token>/",
        views.VerifyAccountTokenAPIView.as_view(),
        name="email_verification_confirm",
    ),
    path(
        "email-verification/resend",
        views.VerificationResendAPIView.as_view(),
        name="email_verification_resend",
    ),
    path("password/reset/", views.PasswordResetAPIView.as_view(), name="password_reset"),
    path("password/reset/confirm/<str:token>/", views.PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
]
