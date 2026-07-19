from rest_framework import permissions

class BaseRolePermission(permissions.BasePermission):
    allowed_roles = []
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        slug = view.kwargs.get('org_slug')
        
        return request.user.org_memberships.filter(
            organization__slug=slug,
            role__in=self.allowed_roles,
        ).exists()
        