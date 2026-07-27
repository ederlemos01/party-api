from rest_framework import serializers
from .models import Event
from .models import EventMember, EventInvite
from .tasks import send_invite_email
from django.db import transaction, IntegrityError
from common.exceptions import UserHasNoAccount, InviteAlreadyExists, AlreadyEventMember
from django.contrib.auth import get_user_model
authuser = get_user_model()


def validate_event(start_at, end_at, organization, slug,instance=None):
    
    if start_at and end_at and start_at >= end_at:
            raise serializers.ValidationError({
               "end_at": "A data de término deve ser estritamente posterior à data de início."
            })


    if organization and slug:
            qs = Event.objects.filter(organization=organization, slug=slug, deleted_at__isnull=True)
            if instance is None:
                slug_is_taken = qs.exists() 
            else:
                slug_is_taken  = qs.exclude(pk = instance.pk).exists()
        
            if slug_is_taken:
                raise serializers.ValidationError({
                    "slug": "ja possui um evento com esse slug na organizacao"
                })
    return




@transaction.atomic
def invite_member(*, event, email, role, invited_by):
    user = authuser.objects.filter(email=email).first()
    if not user:
        raise UserHasNoAccount()       
    
    if EventMember.objects.filter(event=event, user=user).exists():
        raise AlreadyEventMember()
    
    last_invite = EventInvite.objects.filter(event=event, user=user).first()
    if last_invite:
        last_invite.delete()
        
    try:
        invite = EventInvite.objects.create(
            event=event, user=user, role=role, invited_by=invited_by,
        )
    except IntegrityError:
        raise InviteAlreadyExists()
    transaction.on_commit(lambda: send_invite_email.delay(invite.id))
    return invite