from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ...models import Profile
from django.shortcuts import get_object_or_404
from .permissions import IsVerified
from ..utils import EmailVerificationThread
from django.contrib.auth import get_user_model
import jwt
from core.settings import SIMPLE_JWT


User = get_user_model()


class RegistrationAPIView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        EmailVerificationThread(user).start()
        return Response({"email": email}, status=status.HTTP_201_CREATED)


class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "email": user.email}
        )


class DiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ChangePasswordAPIView(GenericAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(
            data=request.data, context={"user": user}
        )

        if serializer.is_valid():
            # Set new password
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()

            return Response(
                {"success": "Password updated successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(Profile, user=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": "Profile updated successfully",
                    "data": serializer.data,
                }
            )

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ActivationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        token = kwargs["token"]
        try:
            token_decoded = jwt.decode(
                token,
                SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[SIMPLE_JWT["ALGORITHM"]],
            )
            user = User.objects.get(id=token_decoded["user_id"])
        except jwt.exceptions.InvalidSignatureError:
            return Response(
                {"detail": "Invalid activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.InvalidSignatureError:
            return Response(
                {"detail": "Invalid activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.ExpiredSignatureError:
            return Response(
                {"detail": "Activation token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.is_verified:
            user.is_verified = True
            user.save()
            return Response(
                {"detail": "Your account has been successfully verified."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Your account is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ActivationResendAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_verified:
            return Response(
                {"detail": "Your account is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        EmailVerificationThread(user).start()
        return Response(
            {"detail": "Verification email sent."}, status=status.HTTP_200_OK
        )
