
from common.permissions import BaseOrganizationRolePermission
from .models import OrganizationRoles

class IsOrganizationManager(BaseOrganizationRolePermission):
    allowed_roles = [OrganizationRoles.MANAGER, OrganizationRoles.OWNER]

class IsOrganizationViewer(BaseOrganizationRolePermission):
    allowed_roles = [OrganizationRoles.VIEWER, OrganizationRoles.MANAGER, OrganizationRoles.OWNER]

class IsOwner(BaseOrganizationRolePermission):
    allowed_roles = [OrganizationRoles.OWNER]