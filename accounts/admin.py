from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationFormAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationFormAdmin
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        # "hijack_button",  # Use a method that provides the hijack button
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login", "date_joined", "groups")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
