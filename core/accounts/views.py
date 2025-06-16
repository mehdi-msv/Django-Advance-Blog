from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    DetailView,
    CreateView,
    RedirectView,
    View,
    FormView,
)
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    LogoutView,
)
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .tasks import send_verification_email, send_password_reset_email
from .models import Profile
from .forms import (
    ProfileUpdateForm,
    UserCreationForm,
    CustomSetPasswordForm,
    CustomPasswordChangeForm,
)
from .utils import ThrottleMixin


User = get_user_model()


class ProfileDetailView(LoginRequiredMixin, FormMixin, DetailView):
    """
    View for displaying and updating the user's profile on the same page.
    Combines DetailView and FormMixin to show profile details and edit form.
    """

    model = Profile
    template_name = "accounts/profile.html"
    context_object_name = "profile"
    form_class = ProfileUpdateForm

    def get_object(self, queryset=None):
        # Returns the current user's profile
        return self.request.user.profile

    def get_success_url(self):
        # Redirect to the same profile page after a successful form submission
        return reverse_lazy("accounts:profile")

    def get_form_kwargs(self):
        # Ensure the form uses the current profile instance
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_object()
        return kwargs

    def post(self, request, *args, **kwargs):
        # Handle form submission
        self.object = (
            self.get_object()
        )  # Required by DetailView to set context
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Save form and show success message
        form.save()
        messages.success(
            self.request, "Your profile has been updated successfully."
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Render form again with error messages
        messages.error(
            self.request,
            "There was an error updating your profile. Please check the form.",
        )
        return self.render_to_response(self.get_context_data(form=form))


class CustomLoginView(ThrottleMixin, LoginView):
    """
    Custom login view for the application.
    This view handles user login with throttling.
    """

    template_name = "accounts/signin.html"
    redirect_authenticated_user = True
    fields = "username", "password"

    throttle_scope = "login"
    throttle_redirect_url = reverse_lazy("accounts:signup")
    throttle_allowed_attempts = 10
    throttle_base_window = 60 * 5  # 5 minutes
    throttle_max_level = 5
    throttle_reset_threshold = 3

    def get(self, request, *args, **kwargs):
        """
        If the user is already authenticated, redirect and show a message.
        """
        if request.user.is_authenticated:
            messages.info(self.request, "You are already logged in.")
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        self.reset_throttle_level()
        next_url = self.request.GET.get("next") or self.request.POST.get(
            "next"
        )
        return next_url or reverse_lazy("blog:post-list")

    def form_invalid(self, form):
        """
        Show error message on invalid login.
        """
        self.record_throttle_attempt()
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


class SignUpView(ThrottleMixin, CreateView):
    """
    Register a new user for the application.
    """

    model = User
    form_class = UserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("blog:post-list")

    throttle_scope = "signup"
    throttle_redirect_url = reverse_lazy("blog:post-list")
    throttle_allowed_attempts = 5
    throttle_base_window = 60 * 10  # 10 minutes
    throttle_max_level = 10
    throttle_reset_threshold = 3

    def get(self, request, *args, **kwargs):
        """
        Check if the user is authenticated before allowing registration.
        """
        if request.user.is_authenticated:
            messages.info(
                self.request, "You are already registered and logged in."
            )
            return redirect(self.success_url)
        return super(SignUpView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Save the new user and log them in after successful registration.
        """
        self.reset_throttle_level()
        self.record_throttle_attempt()
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, "Your account has been created successfully."
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        self.record_throttle_attempt()
        messages.error(
            self.request,
            "There was an error creating your account. Please check the form.",
        )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Custom logout view to display a success message.
    """

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class SendVerificationEmailView(
    LoginRequiredMixin, ThrottleMixin, RedirectView
):
    """
    View to send a verification email to the logged-in user.
    Redirects to the profile page after attempting to send the email.
    """

    permanent = False  # This affects HTTP caching headers; False is typical for dynamic views

    throttle_scope = "verification_email"
    throttle_redirect_url = reverse_lazy("accounts:profile")
    throttle_allowed_attempts = 3
    throttle_base_window = 60 * 5
    throttle_max_level = 5
    throttle_reset_threshold = 3

    def get_redirect_url(self, *args, **kwargs):
        # Redirects to the profile page after the task is triggered
        return reverse_lazy("accounts:profile")

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_verified:
            self.reset_throttle_level()
            # Send the verification email using Celery async task
            send_verification_email.delay(user.id)
            messages.success(
                request, "Verification email has been sent to your email."
            )
        else:
            # Inform the user if already verified
            messages.info(request, "Your email is already verified.")

        self.record_throttle_attempt()
        return super().get(request, *args, **kwargs)


class VerifyAccountTokenView(View):
    """
    View to activate a user's account using a JWT token from the email link.
    """

    def get(self, request, token, *args, **kwargs):
        try:
            # Decode the token using SimpleJWT
            access_token = AccessToken(token)

            # Optional: Check the token purpose to ensure it's for email verification
            if access_token.get("purpose") != "email_verification":
                messages.error(request, "Invalid token purpose.")
                return redirect(reverse_lazy("accounts:login"))

            # Extract user ID from the token payload
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)

        except TokenError:
            # Handle invalid or expired tokens
            messages.error(request, "Invalid or expired activation link.")
            return redirect(reverse_lazy("accounts:profile"))
        except User.DoesNotExist:
            # Handle invalid user references
            messages.error(request, "User does not exist.")
            return redirect(reverse_lazy("accounts:login"))

        if not user.is_verified:
            # Mark user as verified and save
            user.is_verified = True
            user.save()
            messages.success(
                request, "Your account has been successfully verified."
            )
        else:
            # Notify if already verified
            messages.info(request, "Your account is already verified.")

        return redirect(reverse_lazy("accounts:profile"))


class CustomPasswordChangeView(ThrottleMixin, PasswordChangeView):
    """
    Custom view to handle password change requests.
    """

    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    throttle_scope = "password_change"
    throttle_redirect_url = reverse_lazy("accounts:profile")
    throttle_allowed_attempts = 5
    throttle_base_window = 60 * 10  # 10 minutes
    throttle_max_level = 5
    throttle_reset_threshold = 3

    def form_valid(self, form):
        """
        If the form is valid, change the user's password and show a success message.
        """
        self.reset_throttle_level()
        self.record_throttle_attempt()
        messages.success(
            self.request, "Your password has been changed successfully."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, show an error message.
        """
        self.record_throttle_attempt()
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class CustomPasswordResetView(ThrottleMixin, PasswordResetView):
    template_name = "accounts/password_reset.html"
    success_url = reverse_lazy("accounts:login")

    throttle_scope = "password_reset"
    throttle_redirect_url = reverse_lazy("accounts:login")
    throttle_allowed_attempts = 2
    throttle_base_window = 60 * 5  # 5 minutes
    throttle_max_level = 10
    throttle_reset_threshold = 3

    def form_valid(self, form):
        """
        Handle a valid form submission for password reset.
        Sends the reset email asynchronously via Celery task.
        If user with the given email does not exist, show an error message.
        Redirect to success_url after processing.
        """
        email = form.cleaned_data.get("email")
        try:
            # Try to find the user by email
            user = User.objects.get(email=email)
            # Trigger sending password reset email asynchronously
            send_password_reset_email.delay(user.id)
            self.reset_throttle_level()
            messages.success(
                self.request, "Password reset email has been sent."
            )
        except User.DoesNotExist:
            self.record_throttle_attempt()
            # Show error if user not found
            messages.error(
                self.request, "No user found with this email address."
            )

        # Instead of calling super().form_valid(form),
        # directly redirect to the success_url.
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("accounts:login")


class PasswordResetConfirmView(FormView):
    """
    View to handle the password reset confirmation process.
    Validates the reset token, allows the user to set a new password, and handles success and error messages.
    """

    template_name = "accounts/password_reset_confirm.html"
    form_class = CustomSetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides dispatch to retrieve the user based on the token before processing the request.
        This ensures that the user is available to the form and other methods.
        """
        self.user = self.get_user()
        return super().dispatch(request, *args, **kwargs)

    def get_user(self):
        """
        Attempts to decode and validate the password reset token.
        Returns the user associated with the token if valid and intended for password reset; otherwise returns None.
        """
        try:
            token = self.kwargs.get("token")
            access_token = AccessToken(token)
            if access_token.get("purpose") != "password_reset":
                return None
            user_id = access_token["user_id"]
            return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None

    def get_form_kwargs(self):
        """
        Adds the user object to the form kwargs so the form can validate and save the new password for that user.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        """
        Handles valid form submission.
        If the user is valid, saves the new password and shows a success message, then redirects to login.
        If the user is invalid or token expired, shows an error and redirects to login.
        """
        if not self.user:
            messages.error(self.request, "Invalid or expired reset link.")
            return redirect("accounts:login")

        form.save()
        messages.success(
            self.request, "Your password has been reset successfully."
        )
        return redirect("accounts:login")

    def form_invalid(self, form):
        """
        Handles invalid form submission.
        If the user is invalid or token expired, shows an error and redirects to login.
        Otherwise, re-renders the form with validation errors.
        """
        if not self.user:
            messages.error(self.request, "Invalid or expired reset link.")
            return redirect("accounts:login")

        return self.render_to_response(self.get_context_data(form=form))
