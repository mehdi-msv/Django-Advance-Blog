from rest_framework.throttling import BaseThrottle
from rest_framework.exceptions import Throttled
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.core.exceptions import ImproperlyConfigured

from .models.throttle_records import ThrottleRecord


class CustomThrottleException(Throttled):
    """
    Custom exception for throttling with formatted wait time.

    - Extends DRF's Throttled exception.
    - Returns user-friendly message and retry_after value.
    """

    def __init__(self, wait=None):
        formatted = AdaptiveDBThrottle.format_duration(wait)
        super().__init__(
            detail={
                "detail": f"Too many requests. Try again in {formatted}.",
                "retry_after": wait,
            }
        )


class AdaptiveDBThrottle(BaseThrottle):
    """
    Adaptive throttle system using DB per user/IP and scope.

    - Limits allowed attempts per time window.
    - Applies exponential cooldowns with increasing penalty (level).
    """

    def __init__(self, **kwargs):
        """
        Initialize throttle instance with configurable behavior.
        """
        cls = self.__class__
        self.scope = getattr(self, "scope", getattr(cls, "scope", None))
        self.allowed_attempts = getattr(
            self, "allowed_attempts", getattr(cls, "allowed_attempts", 5)
        )
        self.base_window = getattr(
            self, "base_window", getattr(cls, "base_window", 3600)
        )
        self.max_level = getattr(
            self, "max_level", getattr(cls, "max_level", 10)
        )
        self.reset_threshold = getattr(
            self, "reset_threshold", getattr(cls, "reset_threshold", 5)
        )
        self.ident = None
        self.now = None
        self.record = None

    def _init_context(self, request):
        """
        Set client identity and current timestamp.
        Used by all request-related methods.
        """
        self.ident = self.get_ident(request)
        self.now = timezone.now()

    def allow_request(self, request, view):
        """
        Allow request if not blocked, or apply penalty if limits exceeded.
        Raises CustomThrottleException with remaining wait time if blocked.
        """
        self._init_context(request)

        try:
            self.record = ThrottleRecord.objects.get(
                ident=self.ident, scope=self.scope
            )
        except ThrottleRecord.DoesNotExist:
            return True  # First-time access — no restrictions

        if self.record.expires_at > self.now:
            wait_time = int(
                (self.record.expires_at - self.now).total_seconds()
            )
            raise CustomThrottleException(wait=wait_time)

        if self.record.attempts >= self.allowed_attempts:
            cooldown = self.base_window * (2**self.record.level)
            self.record.level = min(self.record.level + 1, self.max_level)
            self.record.attempts = 0  # Reset after penalty
            self.record.expires_at = self.now + timedelta(seconds=cooldown)
            self.record.last_blocked_at = timezone.now()
            self.record.save()

            raise CustomThrottleException(wait=cooldown)

        return True

    def record_attempt(self, request):
        """
        Log a failed attempt. Called after sensitive operations like login.
        """
        self._init_context(request)

        record, created = ThrottleRecord.objects.get_or_create(
            ident=self.ident,
            scope=self.scope,
            defaults={"level": 0, "expires_at": self.now, "attempts": 1},
        )

        if not created and record.expires_at <= self.now:
            record.attempts += 1
            record.save()

    def reset_level(self, request):
        """
        Reset throttle level if user remains blocked for too long.
        """
        self._init_context(request)

        try:
            record = ThrottleRecord.objects.get(
                ident=self.ident, scope=self.scope
            )
            if record.level >= self.reset_threshold:
                record.delete()
        except ThrottleRecord.DoesNotExist:
            pass

    @staticmethod
    def format_duration(seconds):
        """
        Convert seconds into "1h 3m 20s" format for user-friendly display.
        """
        seconds = int(seconds)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)


class APIRegisterThrottle(AdaptiveDBThrottle):
    """
    Throttle for API user registration endpoint.
    Limits to 5 attempts every 10 minutes, with exponential backoff and reset after 3 penalty levels.
    """

    scope = "api_register"
    base_window = 60 * 10
    max_level = 10
    reset_threshold = 3
    allowed_attempts = 5


class APIResetPasswordThrottle(AdaptiveDBThrottle):
    """
    Throttle for API password reset endpoint.
    Allows only 2 attempts every 5 minutes, with exponential cooldown and reset after 3 penalty levels.
    """

    scope = "api_reset_password"
    base_window = 60 * 5
    max_level = 10
    reset_threshold = 3
    allowed_attempts = 2


class APIChangePasswordThrottle(AdaptiveDBThrottle):
    """
    Throttle for authenticated password change endpoint.
    Permits 5 attempts every 10 minutes, with a lower max penalty level of 5 and reset threshold 3.
    """

    scope = "api_change_password"
    base_window = 60 * 10
    max_level = 5
    reset_threshold = 3
    allowed_attempts = 5


class APIVerificationResendThrottle(AdaptiveDBThrottle):
    """
    Throttle for resending email verification endpoint.
    Limits resends to 3 attempts every 5 minutes, with max penalty level 5 and reset threshold 3.
    """

    scope = "api_resend_verification"
    base_window = 60 * 5
    max_level = 5
    reset_threshold = 3
    allowed_attempts = 3


class ThrottleMixin:
    """
    View mixin that integrates adaptive throttling (per-scope).
    Configure by overriding class attributes in the view.
    """

    # Required
    throttle_scope = None
    throttle_redirect_url = None
    throttle_allowed_attempts = None
    throttle_base_window = None
    throttle_max_level = None
    throttle_reset_threshold = None

    def get_throttle_class(self):
        """
        Return the throttle backend class.
        """
        return AdaptiveDBThrottle

    def get_throttle_scope(self):
        """
        Return the configured scope or raise error.
        """
        if not self.throttle_scope:
            raise NotImplementedError(
                "You must define `throttle_scope` in your view."
            )
        return self.throttle_scope

    def get_throttle_redirect_url(self):
        """
        URL to redirect user when throttled.
        """
        return self.throttle_redirect_url or self.request.path

    @cached_property
    def throttle(self):
        """
        Create and configure a throttle instance once per request.
        Uses cached_property to avoid rebuilding multiple times.
        Raises ImproperlyConfigured if required settings are missing.
        """
        required_attrs = [
            "throttle_scope",
            "throttle_allowed_attempts",
            "throttle_base_window",
            "throttle_max_level",
            "throttle_reset_threshold",
        ]

        for attr in required_attrs:
            if getattr(self, attr, None) is None:
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__} is missing required throttle setting: `{attr}`"
                )

        throttle = self.get_throttle_class()()
        throttle.scope = self.get_throttle_scope()
        throttle.allowed_attempts = self.throttle_allowed_attempts
        throttle.base_window = self.throttle_base_window
        throttle.max_level = self.throttle_max_level
        throttle.reset_threshold = self.throttle_reset_threshold
        return throttle

    def dispatch(self, request, *args, **kwargs):
        """
        Apply throttling before calling the original view.
        """
        try:
            self.throttle.allow_request(request, self)
        except CustomThrottleException as e:
            retry_after = self.throttle.format_duration(
                e.detail["retry_after"]
            )
            messages.error(
                request, f"Too many requests! Try again in {retry_after}."
            )
            return redirect(self.get_throttle_redirect_url())

        return super().dispatch(request, *args, **kwargs)

    def record_throttle_attempt(self):
        """
        Log a failed attempt for throttling logic.
        """
        self.throttle.record_attempt(self.request)

    def reset_throttle_level(self):
        """
        Manually reset throttle level if needed.
        """
        self.throttle.reset_level(self.request)


# Maps throttle scope names to their config classes or views.
# Used to fetch throttle settings like `base_window` dynamically.
# API throttles use throttle classes; template-based throttles use view classes.
SCOPE_CONFIG_MAP = {
    "api_register": APIRegisterThrottle,
    "api_reset_password": APIResetPasswordThrottle,
    "api_change_password": APIChangePasswordThrottle,
    "api_resend_verification": APIVerificationResendThrottle,
    "login": "accounts.views.CustomLoginView",
    "signup": "accounts.views.SignUpView",
    "verification_email": "accounts.views.SendVerificationEmailView",
    "password_change": "accounts.views.CustomPasswordChangeView",
    "password_reset": "accounts.views.CustomPasswordResetView",
}
