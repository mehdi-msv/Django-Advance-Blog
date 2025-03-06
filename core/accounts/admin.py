from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_superuser', 'is_staff', 'is_active')
    list_filter = ('email','is_superuser', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ("email",)
    
    fieldsets = (
        ('Authentications', {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
        ('Group Permissions', {'fields': ('groups','user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        ("Registration", {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',),
        }),
        ("Permissions", {
            'classes': ('wide',),
            'fields': ('is_superuser', 'is_staff', 'is_active'),
        }))

admin.site.register(User, CustomUserAdmin)