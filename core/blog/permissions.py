from django.contrib import messages
from django.shortcuts import redirect

class VerifiedUserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.profile.is_verified:
            messages.error(request, "You do not have permission. Your account is not verified.")
            return redirect("accounts:verify")
        return super().dispatch(request, *args, **kwargs)
