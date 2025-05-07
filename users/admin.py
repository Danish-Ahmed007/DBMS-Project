from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model."""
    model = CustomUser
    list_display = ['username', 'email', 'location', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('location',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('location',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
