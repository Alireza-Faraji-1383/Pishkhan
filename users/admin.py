from django.contrib import admin
from .models import VerificationCode, User
from django.contrib.auth import admin as auth_admin

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    list_display = ('username', 'email','role', 'is_active')
    
    search_fields = ('username', 'first_name', 'last_name', 'email', 'role')
    
    fieldsets =  (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('مجوز ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخچه', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('مجوز ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    readonly_fields = ('last_login', 'date_joined')

    search_fields = ('username', 'first_name', 'last_name', 'email', 'role')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(VerificationCode)