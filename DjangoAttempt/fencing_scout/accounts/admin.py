from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')

admin.site.register(CustomUser, CustomUserAdmin)
