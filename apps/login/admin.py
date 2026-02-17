"""
Configuración del admin para la aplicación login.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.TabularInline):
    """Mostrar UserProfile en línea dentro del admin de User."""
    model = UserProfile
    extra = 0


class CustomUserAdmin(UserAdmin):
    """Extiende el admin de User con el perfil."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para UserProfile."""
    model = UserProfile
    list_display = ['user', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'role', 'is_verified')
        }),
        ('Información Personal', {
            'fields': ('bio', 'avatar', 'phone', 'date_of_birth')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Reemplazar el admin de User con el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

