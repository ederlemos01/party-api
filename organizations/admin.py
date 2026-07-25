from django.contrib import admin
from .models import (
    Organization,
    OrganizationMember,
    OrganizationInvite,
    OrganizationFollow,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'owner__username', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'created_at')
    search_fields = ('user__username', 'user__email', 'organization__name')
    list_filter = ('role',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(OrganizationInvite)
class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'status', 'expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'organization__name')
    list_filter = ('status', 'role')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(OrganizationFollow)
class OrganizationFollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'created_at')
    search_fields = ('user__username', 'user__email', 'organization__name')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
