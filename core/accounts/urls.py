from django.urls import path, include
from .views import ProfileDetailView, CustomLoginView, SignUpView
app_name = "accounts"


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("api/v1/", include("accounts.api.v1.urls")),
    path("api/v2/", include("djoser.urls")),
    path("api/v2/", include("djoser.urls.jwt")),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("sign-in/", CustomLoginView.as_view(), name="login"),
    path("sign-up/", SignUpView.as_view(), name="signup"),
]
