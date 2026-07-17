
from common.permissions import BaseRolePermission
from .models import Roles

class IsManager(BaseRolePermission):
    allowed_roles = [Roles.MANAGER, Roles.OWNER]

class IsViewer(BaseRolePermission):
    allowed_roles = [Roles.VIEWER, Roles.MANAGER, Roles.OWNER]