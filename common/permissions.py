from rest_framework import permissions

class BaseOrganizationRolePermission(permissions.BasePermission):
    allowed_roles = []
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        slug = view.kwargs.get('org_slug')
        
        return request.user.org_memberships.filter(
            organization__slug=slug,
            role__in=self.allowed_roles,
        ).exists()



class BaseEventRolePermission(permissions.BasePermission):
    allowed_roles = []
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        event_slug = view.kwargs.get('event_slug')
        organization_slug = view.kwargs.get('org_slug')
        return request.user.event_memberships.filter(
            event__organization__slug=organization_slug ,
            event__slug=event_slug,
            role__in=self.allowed_roles,
        ).exists()
        