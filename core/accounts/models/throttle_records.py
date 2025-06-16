from django.db import models


class ThrottleRecord(models.Model):
    ident = models.CharField(max_length=255, help_text="User ID or IP")
    scope = models.CharField(
        max_length=100,
        help_text="Throttle type, e.g., 'changepassword', 'register'",
    )
    level = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    last_blocked_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scope} → {self.ident} (level {self.level})"

    class Meta:
        unique_together = ("ident", "scope")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["ident", "scope"]),
        ]
