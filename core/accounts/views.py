from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login

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