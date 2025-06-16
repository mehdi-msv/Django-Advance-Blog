from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth import password_validation
from .models import Profile


User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    """
    A simple form for updating user profile information.
    """

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "description", "image"]


class UserCreationForm(forms.ModelForm):
    """
    A custom form for creating users. Includes an email field and two password fields,
    with validation to ensure they match and secure password setting.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email"]

    def clean_password2(self):
        """
        Validates that the two entered passwords match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """
        Saves the user instance with a hashed password.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    A custom password change form that prevents using the old password as the new password.
    """

    def clean_new_password1(self):
        """
        Ensures that the new password is different from the old password.
        """
        new_password = self.cleaned_data.get("new_password1")
        old_password = self.cleaned_data.get("old_password")

        if old_password and new_password and old_password == new_password:
            raise forms.ValidationError(
                _("Your new password cannot be the same as the old password.")
            )
        return new_password


class CustomSetPasswordForm(DjangoSetPasswordForm):
    """
    A custom set password form used when resetting a user's password.
    Includes validation for password strength and confirmation.
    """

    def clean_new_password1(self):
        """
        Validates that the new password is provided and meets password policy.
        """
        password1 = self.cleaned_data.get("new_password1")
        if not password1:
            raise forms.ValidationError(_("New password is required."))

        try:
            password_validation.validate_password(password1, self.user)
        except forms.ValidationError as error:
            raise forms.ValidationError(error.messages)

        return password1

    def clean_new_password2(self):
        """
        Ensures that the confirmation password matches the new password.
        """
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if not password2:
            raise forms.ValidationError(
                _("Please confirm your new password.")
            )

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The two passwords do not match."))

        return password2
