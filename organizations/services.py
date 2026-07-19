from .models import OrganizationInvite, OrganizationMember
from .tasks import send_invite_email
from django.db import transaction, IntegrityError
from .exceptions import UserHasNoAccount, InviteAlreadyExists, AlreadyMember
from django.contrib.auth import get_user_model
authuser = get_user_model()


@transaction.atomic
def invite_member(*, org, email, role, invited_by):
    user = authuser.objects.filter(email=email).first()
    if not user:
        raise UserHasNoAccount()       
    
    if OrganizationMember.objects.filter(organization=org, user=user).exists():
        raise AlreadyMember()
    
    last_invite = OrganizationInvite.objects.filter(organization=org, user=user).first()
    if last_invite:
        last_invite.delete()
        
    try:
        invite = OrganizationInvite.objects.create(
            organization=org, user=user, role=role, invited_by=invited_by,
        )
    except IntegrityError:
        raise InviteAlreadyExists()
    transaction.on_commit(lambda: send_invite_email.delay(invite.id))
    return invite


