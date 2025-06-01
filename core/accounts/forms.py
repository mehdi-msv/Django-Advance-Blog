from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, User


User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'description', 'image']




class UserCreationForm(forms.ModelForm):
    """
    A custom form for creating users. Includes all required fields,
    plus a repeated password check.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user