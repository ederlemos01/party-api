from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'birth_date', 'is_private', 'date_joined',
                    'updated_at', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'is_private')
    readonly_fields = ('last_login', 'date_joined', 'updated_at')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Perfil', {'fields': ('photo', 'bio', 'birth_date', 'is_private')}),
        ('Auditoria', {'fields': ('updated_at',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'usable_password', 'password1', 'password2'),
        }),
    )
