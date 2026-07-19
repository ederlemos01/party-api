from celery import shared_task
from .models import OrganizationInvite
from django.core.mail import send_mail
from django.conf import settings



@shared_task
def send_invite_email(invite_id):
    invite = (
        OrganizationInvite.objects
        .select_related("organization", "user")
        .filter(pk=invite_id)
        .first()
    )
    if invite is None:
        return  

    context = {
        "org_name": invite.organization.name,
        "accept_url": f"frontendurlexample/organization/invite/{invite.id}",
    }
    
    send_mail(
        subject=f"Convite para {invite.organization.name}",
        message=f"Voce foi convidado apra ser {invite.role}, para aceitar acesse {context["accept_url"]}.",
        from_email= settings.DEFAULT_FROM_EMAIL ,
        recipient_list=[invite.user.email],
        fail_silently=False,
        )