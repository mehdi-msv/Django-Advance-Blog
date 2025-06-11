from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from django.core.exceptions import ValidationError as DjangoValidationError

from ...models import User, Profile


class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating users using email and password.
    """

    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        """
        Validate the user credentials using Django's `authenticate`.
        """
        username = attrs.get("email")
        password = attrs.get("password")

        if username and password:
            # Authenticate the user
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            # Check if authentication failed
            if not user:
                raise serializers.ValidationError(
                    _("Unable to log in with provided credentials."),
                    code="authorization"
                )
        else:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
                code="authorization"
            )

        attrs["user"] = user
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. Validates matching passwords and enforces password strength.
    """
    password1 = serializers.CharField(
        max_length=255, write_only=True, help_text="Password confirmation."
    )

    class Meta:
        model = User
        fields = ["email", "password", "password1"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        """
        Ensure both passwords match and validate password strength.
        """
        if attrs["password"] != attrs["password1"]:
            raise serializers.ValidationError({"password": "Passwords must match."})

        try:
            validate_password(attrs["password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return super().validate(attrs)

    def create(self, validated_data):
        """
        Create a new user instance with hashed password.
        """
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens.
    Adds user-specific claims to the token response
    and prevents login if the user is not verified.
    """

    def validate(self, attrs):
        """
        Validates the user credentials and checks if the user is verified.
        Adds additional user information to the response if authentication succeeds.

        Args:
            attrs (dict): The input data containing username and password.

        Returns:
            dict: A dictionary containing access/refresh tokens and extra user data.

        Raises:
            serializers.ValidationError: If the user is not verified.
        """
        validated_data = super().validate(attrs)

        # Prevent login if the user has not verified their email
        if not self.user.is_verified:
            raise serializers.ValidationError(
                {"detail": "User account is not verified."}
            )

        # Add extra user information to the token response
        validated_data["email"] = self.user.email
        validated_data["user_id"] = self.user.id

        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer to validate and process user password change requests.
    Enforces:
    - Old password correctness
    - Password confirmation match
    - Password complexity via Django validators
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context["user"]

        # Check if old password is correct
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({
                "old_password": _("Incorrect old password.")
            })

        # Prevent using the same password again
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": _("New password cannot be the same as the old password.")
            })

        # Check if new password and confirmation match
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": _("Passwords do not match.")
            })

        # Validate new password using Django's built-in validators
        try:
            validate_password(attrs["new_password"], user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({
                "new_password": list(e.messages)
            })

        return attrs


# Regex pattern to validate names (only alphabetic characters and spaces)
name_regex = re.compile(r"^[A-Za-z\s]+$")


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    Includes validation for first and last names to contain only letters and spaces.
    """
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "email", "first_name", "last_name", "description", "image"]

    def validate_first_name(self, value):
        """
        Ensure the first name contains only alphabetic characters and spaces.
        """
        if not name_regex.match(value):
            raise serializers.ValidationError("First name must contain only letters and spaces.")
        return value

    def validate_last_name(self, value):
        """
        Ensure the last name contains only alphabetic characters and spaces.
        """
        if not name_regex.match(value):
            raise serializers.ValidationError("Last name must contain only letters and spaces.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset.
    Uses Django's built-in password validators to ensure password strength.
    """
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Ensure both entered passwords match and meet Django's password strength requirements.
        """
        password1 = attrs.get('new_password1')
        password2 = attrs.get('new_password2')

        if password1 != password2:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            validate_password(password1)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password1': list(e.messages)})

        return attrs

    def save(self, user):
        """
        Set the new password for the given user.
        """
        user.set_password(self.validated_data['new_password1'])
        user.save()
