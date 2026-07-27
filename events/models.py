from django.db import models
from common.models import BaseModel
from organizations.models import Organization
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.conf import settings
from .validators import validate_slug
from datetime import timedelta
from django.utils import timezone
from common.exceptions import NotInvitedUser, InviteExpired, InviteNotPending, AlreadyEventMember

class EventStatus(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        PUBLISHED = 'published', 'Publicado'
        FINISHED = 'finished','Finalizado'
        CANCELED = 'canceled', 'Cancelado'

        
class Event(BaseModel):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT,related_name='events')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True,
        validators=[MaxLengthValidator(1000)]
    )
    banner = models.ImageField(upload_to='events/banner/', blank=True,  max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length= 20, choices=EventStatus.choices, default=EventStatus.DRAFT)
    slug = models.SlugField(validators=[MinLengthValidator(limit_value=2,),validate_slug],)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['slug','organization'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_active_organization_and_slug',
            ),models.CheckConstraint(condition=models.Q(end_at__gt=models.F('start_at')), 
                                     name='event_end_after_start')]
        

    def __str__(self):
        return f'{self.organization} - {self.title}'

class EventRoles(models.TextChoices):
    MANAGER = "manager", "Gerente"
    CHECKIN_COORDINATOR = "checkin_coordinator", "Coordenador de check-in"
    VIEWER = "viewer", "Visualizador"


class EventMember(BaseModel):
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            editable=False,
            related_name='event_memberships',
         )
    event = models.ForeignKey(
            Event,
            on_delete=models.CASCADE,
            editable=False,
            related_name='members',
            )
    role = models.CharField(max_length=32, choices=EventRoles.choices)

    class Meta(BaseModel.Meta):
            constraints = [
                models.UniqueConstraint(
                    fields=['user', 'event'],
                    condition=models.Q(deleted_at__isnull=True),
                    name='unique_active_event_member',
                ),
            ]
    
    def __str__(self):
        return f'{self.user} @ {self.event} ({self.role})'

def expiration_date():
    return timezone.now() + timedelta(days=7)

class EventInvite(BaseModel):
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='sent_event_invites',
                                   editable=False,)
    event = models.ForeignKey(Event,editable=False,
                                     on_delete=models.CASCADE,related_name='event_invites',)
    role = models.CharField(max_length=32, choices=EventRoles.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='received_event_invites',)
    
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceito'
        REVOKED = 'revoked', 'Cancelado'
        EXPIRED = 'expired', 'Expirado'

    status = models.CharField(max_length=20,choices=StatusChoices.choices,default=StatusChoices.PENDING,)
        
    
    expires_at = models.DateTimeField(default=expiration_date)


    
    def __str__(self):
        return f'{self.user} + {self.event} + {self.role}'
    
    class Meta(BaseModel.Meta):
        constraints = [ models.UniqueConstraint(fields=['user', 'event'],
                                                    condition=models.Q(status='pending') & models.Q(deleted_at__isnull=True),
                                                    name= 'unique_event_invite_pending')]
        
    def delete(self, *args, **kwargs):
        self.status = EventInvite.StatusChoices.REVOKED
        self.save(update_fields=['status'])
        return super().delete(*args, **kwargs)
    
    @property
    def is_expired(self):
        return self.expires_at < timezone.now()
    
    def accept(self, by_user):
        if self.user_id != by_user.id:
            raise NotInvitedUser()
        if self.is_expired:            
            raise InviteExpired()
        if self.status != self.StatusChoices.PENDING:
            raise InviteNotPending()   
        member, created = EventMember.objects.get_or_create(
            user=self.user, event=self.event,
            defaults={'role': self.role},
        )
        if not created:
            raise AlreadyEventMember()
        self.status = self.StatusChoices.ACCEPTED
        self.save(update_fields=['status', 'updated_at'])
        return member


