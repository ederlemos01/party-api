from rest_framework import permissions

class BaseRolePermission(permissions.BasePermission):
    allowed_roles = []
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        my_org = getattr(obj, 'organization', obj)
        membership = request.user.org_memberships.filter(organization=my_org).first()
        if not membership:
            return False
        return membership.role in self.allowed_roles