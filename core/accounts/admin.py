from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from .models.throttle_records import ThrottleRecord

# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "is_superuser",
        "is_staff",
        "is_active",
        "is_verified",
    )
    list_filter = (
        "email",
        "is_superuser",
        "is_staff",
        "is_active",
        "is_verified",
    )
    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (
        ("Authentications", {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_verified",
                )
            },
        ),
        ("Group Permissions", {"fields": ("groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            "Registration",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("wide",),
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_verified",
                ),
            },
        ),
    )


@admin.register(ThrottleRecord)
class ThrottleRecordAdmin(admin.ModelAdmin):
    list_display = ("scope", "ident", "level", "expires_at", "updated_at")
    search_fields = ("ident", "scope")
    list_filter = ("scope",)
    ordering = ("-updated_at",)


admin.site.register(Profile)
admin.site.register(User, CustomUserAdmin)
