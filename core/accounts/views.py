from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .models import Profile
from .forms import ProfileUpdateForm


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

    