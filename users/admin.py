from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from .models import VerificationCode, User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """Admin configuration for the email-based custom User model."""

    list_display = ('email', 'role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'role')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'role')}),
        ('مجوزها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخچه', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'role')}),
        ('مجوزها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    readonly_fields = ('last_login', 'date_joined')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(VerificationCode)
