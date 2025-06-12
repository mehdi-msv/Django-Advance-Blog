from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.parsers import MultiPartParser, FormParser

from ...utils import (
    APIChangePasswordThrottle,
    APIResetPasswordThrottle,
    APIRegisterThrottle,
    APIVerificationResendThrottle
    )
from ...models import Profile
from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    PasswordResetConfirmSerializer,
    )
from ...tasks import send_verification_email, send_password_reset_email


User = get_user_model()


class RegistrationAPIView(GenericAPIView):
    """
    API endpoint for user registration.

    - Accepts: email, password, password1
    - Validates password strength and sends verification email asynchronously.
    - Returns: 201 Created with email on success
    - Only accessible to unauthenticated users.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [APIRegisterThrottle]

    def post(self, request, *args, **kwargs):
        throttle = self.get_throttles()[0]
        throttle.record_attempt(request)

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Send verification email asynchronously
        send_verification_email.delay(user.id)
        throttle.reset_level(request)
        return Response({"email": email}, status=status.HTTP_201_CREATED)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    API endpoint for obtaining an authentication token using email and password.

    - Accepts email/password
    - Returns token, user ID, and email
    - Compatible with TokenAuthentication
    """
    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to authenticate user and return auth token.
        """
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.pk,
            "email": user.email
        })


class DiscardAuthToken(APIView):
    """
    API endpoint to manually invalidate (delete) a user's authentication token.

    - Requires the user to be authenticated.
    - Deletes the associated token to log the user out from token-based sessions.
    - Returns HTTP 200 on success.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Handle POST request to discard the current user's authentication token.
        """
        # Delete the user's current token (token-based logout)
        request.user.auth_token.delete()

        # Respond with success status
        return Response(
            {"detail": _("Token discarded successfully.")},
            status=status.HTTP_200_OK
        )


class ChangePasswordAPIView(GenericAPIView):
    """
    API endpoint for allowing authenticated users to change their password.

    Features:
    - Requires authentication (IsAuthenticated)
    - Applies custom throttle to limit password change frequency
    - Validates current password, confirmation, and strength
    - Uses Django's password validation system for security enforcement
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [APIChangePasswordThrottle]

    def put(self, request, *args, **kwargs):
        throttle = self.get_throttles()[0]
        throttle.record_attempt(request)
        user = request.user

        # Initialize serializer with request data and user context
        serializer = self.get_serializer(
            data=request.data,
            context={"user": user}
        )

        if not serializer.is_valid():
            # Return validation errors if input is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Set the new validated password and save the user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        throttle.reset_level(request)
        # Return success response upon password change
        return Response(
            {"success": _("Password updated successfully.")},
            status=status.HTTP_200_OK
        )


class ProfileAPIView(RetrieveUpdateAPIView):
    """
    API endpoint that allows authenticated users to retrieve and update their profile.

    - GET:    Retrieve the current user's profile data.
    - PUT:    Fully update the user's profile.
    - PATCH:  Partially update the user's profile.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        """
        Returns the profile instance of the currently authenticated user.
        """
        return get_object_or_404(Profile, user=self.request.user)

    def perform_update(self, serializer):
        """
        Hook for performing custom actions when saving the updated profile.
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Handles PUT and PATCH requests to update the authenticated user's profile.

        Returns a custom success message and the updated profile data upon success.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": _("Profile updated successfully."),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyAccountTokenAPIView(APIView):
    """
    API view to verify user's account via token.
    """
    permission_classes = [AllowAny]

    def get(self, request, token, *args, **kwargs):
        try:
            # Decode the token
            access_token = AccessToken(token)

            # Ensure token purpose is email verification
            if access_token.get("purpose") != "email_verification":
                return Response(
                    {"detail": _("Invalid token purpose.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get user from token payload
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)

        except TokenError:
            return Response(
                {"detail": _("Invalid or expired activation link.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": _("User does not exist.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If user is already verified
        if user.is_verified:
            return Response(
                {"detail": _("Your account is already verified.")},
                status=status.HTTP_200_OK,
            )

        # Verify the user
        user.is_verified = True
        user.save()

        return Response(
            {"detail": _("Your account has been successfully verified.")},
            status=status.HTTP_200_OK,
        )


class VerificationResendAPIView(APIView):
    """
    Resend verification email with a custom 5-minute cooldown per user.
    Uses both custom cooldown and DRF global throttling.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [APIVerificationResendThrottle]
    
    def post(self, request, *args, **kwargs):
        throttle = self.get_throttles()[0]
        throttle.record_attempt(request)
        user = request.user

        if user.is_verified:
            return Response(
                {"detail": _("Your account is already verified.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_verification_email.delay(user.id)
        throttle.reset_level(request)
        return Response(
            {"detail": _("Verification email sent successfully.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetAPIView(APIView):
    """
    API view to request a password reset. Accepts an email and triggers an async email task.
    """
    permission_classes = [AllowAny]
    throttle_classes = [APIResetPasswordThrottle]

    def post(self, request):
        throttle = self.get_throttles()[0]
        throttle.record_attempt(request)
        
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            send_password_reset_email.delay(user.id)
            throttle.reset_level(request)
            return Response({"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "No user found with this email address."}, status=status.HTTP_404_NOT_FOUND)

        
class PasswordResetConfirmAPIView(APIView):
    """
    API endpoint to confirm password reset with token and set a new password.
    """
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            access_token = AccessToken(token)
            if access_token.get('purpose') != 'password_reset':
                return Response({"detail": "Invalid token purpose."}, status=status.HTTP_400_BAD_REQUEST)

            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
