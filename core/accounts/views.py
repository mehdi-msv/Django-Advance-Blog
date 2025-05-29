from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Profile
from .forms import ProfileUpdateForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.score = self.request.user.profile.score
        return super().form_valid(form)
