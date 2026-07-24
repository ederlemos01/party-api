from common.permissions import BaseEventRolePermission
from .models import EventRoles

class IsManager(BaseEventRolePermission):
    allowed_roles = [EventRoles.MANAGER]

class IsCheckinCoordinator(BaseEventRolePermission):
    allowed_roles = [EventRoles.CHECKIN_COORDINATOR,EventRoles.MANAGER ]
    
class IsViewer(BaseEventRolePermission):
    allowed_roles = [EventRoles.VIEWER, EventRoles.CHECKIN_COORDINATOR,EventRoles.MANAGER]

