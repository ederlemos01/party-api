from django.db import models
from common.models import BaseModel
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .validators import validate_slug
import uuid
from .exceptions import InviteExpired, NotInvitedUser, AlreadyMember,InviteNotPending
class Roles(models.TextChoices):
    OWNER = "owner", "Dono"
    MANAGER = "manager", "Gerente" 
    VIEWER = "viewer", "Visualizador"
    CHECKIN = "checkin", "Check-in"
    COORDENADOR_CHECKIN = "coordenador_checkin", "Coordenador de check-in"

class Organization(BaseModel):
    name = models.CharField(blank=True,max_length=100)
    description = models.TextField(blank=True,
        validators=[MaxLengthValidator(1000)]
    )
    photo = models.ImageField(upload_to='organizations/photos/', blank=True,  max_length=255)
    banner = models.ImageField(upload_to='organizations/banners/', blank=True,  max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='owned_organizations')
    
    slug = models.SlugField(validators=[MinLengthValidator(limit_value=2,),validate_slug],default=uuid.uuid4)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['slug'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_active_organization_slug',
            ),models.UniqueConstraint(
                fields=['owner'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_active_organization_owner',
            ),
        ]

    def __str__(self):
        return self.name


class OrganizationFollow(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_follows',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='follows',
    )

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization'],
                name='unique_organization_follow',
            ),
        ]


class OrganizationMember(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
        related_name='org_memberships',
    )
    organization = models.ForeignKey(
        Organization,
        editable=False,
        on_delete=models.CASCADE,
        related_name='members',
    )


    role = models.CharField(max_length=32, choices=Roles.choices)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_active_organization_member',
            ),
        ]

    def __str__(self):
        return f'{self.user} @ {self.organization} ({self.role})'






def expiration_date():
    return timezone.now() + timedelta(days=7)

class OrganizationInvite(BaseModel):
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='sent_invites',
                                   editable=False,)
    organization = models.ForeignKey(Organization,editable=False,
                                     on_delete=models.CASCADE,related_name='invites',)
    role = models.CharField(max_length=32, choices=Roles.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='received_invites',)
    
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceito'
        REVOKED = 'revoked', 'Cancelado'
        EXPIRED = 'expired', 'Expirado'

    status = models.CharField(max_length=20,choices=StatusChoices.choices,default=StatusChoices.PENDING,)
        
    
    expires_at = models.DateTimeField(default=expiration_date)


    
    def __str__(self):
        return f'{self.user} + {self.organization} + {self.role}'
    
    class Meta(BaseModel.Meta):
        constraints = [ models.UniqueConstraint(fields=['user', 'organization'],
                                                    condition=models.Q(status='pending') & models.Q(deleted_at__isnull=True),
                                                    name= 'unique_invite_pending')]
        
    def delete(self, *args, **kwargs):
        self.status = OrganizationInvite.StatusChoices.REVOKED
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
        member, created = OrganizationMember.objects.get_or_create(
            user=self.user, organization=self.organization,
            defaults={'role': self.role},
        )
        if not created:
            raise AlreadyMember()
        self.status = self.StatusChoices.ACCEPTED
        self.save(update_fields=['status', 'updated_at'])
        return member