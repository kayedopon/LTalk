from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin) : 
    list_display = ("email" , "id", "username" , "date_joined", "last_login" , "is_active" , "is_staff", "is_superuser" )
    search_fields = ("email" , "username", "id")
    readonly_fields = ("id" , "date_joined" , "last_login")
    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )

admin.site.register(User, UserAdmin)