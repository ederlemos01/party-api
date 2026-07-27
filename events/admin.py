from django.contrib import admin
from .models import Event, EventMember,EventInvite


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'status', 'start_at', 'end_at', 'created_at')
    search_fields = ('title', 'slug', 'organization__name', 'location')
    list_filter = ('status', 'start_at')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(EventMember)
class EventMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'role', 'created_at')
    search_fields = ('user__username', 'user__email', 'event__title')
    list_filter = ('role',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')


@admin.register(EventInvite)
class EventInviteAdmin(admin.ModelAdmin):

    list_display = ('user', 'event', 'role', 'status', 'invited_by', 'expires_at')
    

    search_fields = (
        'user__username', 
        'user__email', 
        'event__title', 
        'invited_by__username', 
        'invited_by__email'
    )
    list_filter = ('status', 'role')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')