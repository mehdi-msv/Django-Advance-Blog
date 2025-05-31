from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin

class VerifiedUserRequiredMixin(AccessMixin):
    """
    Mixin to ensure that the user is authenticated and verified.
    If not, they are redirected to the verification page with an error message.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not getattr(request.user, "is_verified", False):
            messages.error(request, "Your account is not verified.")
            return redirect("accounts:verify")

        return super().dispatch(request, *args, **kwargs)
