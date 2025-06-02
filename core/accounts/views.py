from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, RedirectView, View
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .tasks import send_verification_email
from .models import Profile
from .forms import ProfileUpdateForm, UserCreationForm



User = get_user_model()


class ProfileDetailView(LoginRequiredMixin, FormMixin, DetailView):
    """
    View for displaying and updating the user's profile on the same page.
    Combines DetailView and FormMixin to show profile details and edit form.
    """
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'
    form_class = ProfileUpdateForm

    def get_object(self, queryset=None):
        # Returns the current user's profile
        return self.request.user.profile

    def get_success_url(self):
        # Redirect to the same profile page after a successful form submission
        return reverse_lazy('profile')

    def get_form_kwargs(self):
        # Ensure the form uses the current profile instance
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def post(self, request, *args, **kwargs):
        # Handle form submission
        self.object = self.get_object()  # Required by DetailView to set context
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Save form and show success message
        form.save()
        messages.success(self.request, "Your profile has been updated successfully.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Render form again with error messages
        messages.error(self.request, "There was an error updating your profile. Please check the form.")
        return self.render_to_response(self.get_context_data(form=form))


class CustomLoginView(LoginView):
    """
    Custom login view for the application.
    """

    template_name = "accounts/signin.html"
    redirect_authenticated_user = True
    fields = "username", "password"
    success_url = reverse_lazy("blog:post-list")
    
    def get(self, request, *args, **kwargs):
        """
        If the user is already authenticated, redirect and show a message.
        """
        if request.user.is_authenticated:
            messages.info(self.request, "You are already logged in.")
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        """
        Show error message on invalid login.
        """
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

class SignUpView(CreateView):
    """
    Register a new user for the application.
    """

    model = User
    form_class = UserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("blog:post-list")

    def get(self, request, *args, **kwargs):
        """
        Check if the user is authenticated before allowing registration.
        """
        if request.user.is_authenticated:
            messages.info(self.request, "You are already registered and logged in.")
            return redirect(self.success_url)
        return super(SignUpView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Save the new user and log them in after successful registration.
        """
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Your account has been created successfully.")
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, "There was an error creating your account. Please check the form.")
        return super().form_invalid(form)


class SendVerificationEmailView(LoginRequiredMixin, RedirectView):
    """
    View to send a verification email to the logged-in user.
    Redirects to the profile page after attempting to send the email.
    """
    permanent = False  # This affects HTTP caching headers; False is typical for dynamic views

    def get_redirect_url(self, *args, **kwargs):
        # Redirects to the profile page after the task is triggered
        return reverse_lazy('accounts:profile')

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_verified:
            # Send the verification email using Celery async task
            send_verification_email.delay(user.id)
            messages.success(request, 'Verification email has been sent to your inbox.')
        else:
            # Inform the user if already verified
            messages.info(request, 'Your email is already verified.')

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
            if access_token.get('purpose') != 'email_verification':
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
            messages.success(request, "Your account has been successfully verified.")
        else:
            # Notify if already verified
            messages.info(request, "Your account is already verified.")

        return redirect(reverse_lazy("accounts:profile"))
