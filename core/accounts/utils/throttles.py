from rest_framework.throttling import BaseThrottle
from rest_framework.exceptions import Throttled
from django.utils import timezone
from datetime import timedelta

from ..models.throttle_records import ThrottleRecord


class CustomThrottleException(Throttled):
    """
    Custom exception for throttling with formatted wait time.

    - Extends DRF's Throttled exception.
    - Returns user-friendly message and retry_after value.
    """
    def __init__(self, wait=None):
        formatted = AdaptiveDBThrottle.format_duration(wait)
        super().__init__(detail={
            "detail": f"Too many requests. Try again in {formatted}.",
            "retry_after": wait
        })


class AdaptiveDBThrottle(BaseThrottle):
    """
    Adaptive throttle system using DB per user/IP and scope.
    
    - Limits allowed attempts per time window.
    - Applies exponential cooldowns with increasing penalty (level).
    """

    scope = None
    base_window = 60 * 60  # 1 hour
    max_level = 10
    reset_threshold = 5
    allowed_attempts = 5

    def _init_context(self, request):
        """
        Ensure ident and current time are initialized.
        Useful when other methods are called before allow_request.
        """
        self.ident = getattr(self, 'ident', self.get_ident(request))
        self.now = getattr(self, 'now', timezone.now())

    def allow_request(self, request, view):
        """
        Allow request if not throttled or if attempts are within allowed range.
        Raises a custom exception with readable wait time if blocked.
        """
        self._init_context(request)

        try:
            self.record = ThrottleRecord.objects.get(ident=self.ident, scope=self.scope)
        except ThrottleRecord.DoesNotExist:
            return True  # No record yet, allow request

        if self.record.expires_at > self.now:
            wait_time = int((self.record.expires_at - self.now).total_seconds())
            raise CustomThrottleException(wait=wait_time)

        if self.record.attempts >= self.allowed_attempts:
            cooldown = self.base_window * (2 ** self.record.level)

            if self.record.expires_at <= self.now:
                self.record.level = min(self.record.level + 1, self.max_level)
                self.record.attempts = 0  # Reset after penalty

            self.record.expires_at = self.now + timedelta(seconds=cooldown)
            self.record.save()
            raise CustomThrottleException(wait=cooldown)

        return True

    def wait(self):
        """
        Return remaining wait time in seconds (used internally).
        """
        return getattr(self, 'wait_seconds', 0)

    def record_attempt(self, request):
        """
        Log a new attempt after sensitive actions (e.g., login, registration).
        """
        self._init_context(request)

        record, created = ThrottleRecord.objects.get_or_create(
            ident=self.ident,
            scope=self.scope,
            defaults={
                "level": 0,
                "expires_at": self.now,
                "attempts": 1
            }
        )

        if not created:
            if record.expires_at <= self.now:
                record.attempts += 1
            record.save()

    def reset_level(self, request):
        """
        Reset throttle record if user is blocked repeatedly.
        """
        self._init_context(request)
        try:
            record = ThrottleRecord.objects.get(ident=self.ident, scope=self.scope)
            if record.level >= self.reset_threshold:
                record.delete()
        except ThrottleRecord.DoesNotExist:
            pass

    @staticmethod
    def format_duration(seconds):
        """
        Format seconds as "1h 3m 20s" for better readability.
        """
        seconds = int(seconds)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        return ' '.join(parts)


class RegisterThrottle(AdaptiveDBThrottle):
    scope = 'register'
    base_window = 60 * 30
    max_level = 10
    reset_threshold = 3
    allowed_attempts = 3


class ResetPasswordThrottle(AdaptiveDBThrottle):
    scope = 'reset_password'
    base_window = 60 * 10
    max_level = 10
    reset_threshold = 3
    allowed_attempts = 2


class ChangePasswordThrottle(AdaptiveDBThrottle):
    scope = 'change_password'
    base_window = 60
    max_level = 5
    reset_threshold = 3
    allowed_attempts = 3


class VerificationResendThrottle(AdaptiveDBThrottle):
    scope = 'resend_verification'
    base_window = 60 * 5
    max_level = 5
    reset_threshold = 2
    allowed_attempts = 3
