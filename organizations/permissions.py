
from common.permissions import BaseOrganizationRolePermission
from .models import OrganizationRoles

class IsManager(BaseOrganizationRolePermission):
    allowed_roles = [OrganizationRoles.MANAGER, OrganizationRoles.OWNER]

class IsViewer(BaseOrganizationRolePermission):
    allowed_roles = [OrganizationRoles.VIEWER, OrganizationRoles.MANAGER, OrganizationRoles.OWNER]

class IsOwner(BaseOrganizationRolePermission):
    allowed_roles = [OrganizationRoles.OWNER]