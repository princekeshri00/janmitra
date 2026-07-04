from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "phone_number",
        "preferred_language",
        "is_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_verified",
        "preferred_language",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone_number",
        "firebase_uid",
    )

    ordering = (
        "-date_joined",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "JanMitra",
            {
                "fields": (
                    "firebase_uid",
                    "role",
                    "phone_number",
                    "preferred_language",
                    "is_verified",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "JanMitra",
            {
                "fields": (
                    "email",
                    "role",
                    "phone_number",
                    "preferred_language",
                    "is_verified",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "date_joined",
        "last_login",
    )