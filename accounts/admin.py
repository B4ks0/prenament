from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'nama_lengkap')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('role', 'nama_lengkap')}),
    )
    list_display = ('username', 'email', 'role', 'nama_lengkap')
    list_filter = BaseUserAdmin.list_filter + ('role',)
