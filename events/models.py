from django.db import models
from common.models import BaseModel
from organizations.models import Organization
from django.core.validators import MaxLengthValidator, MinLengthValidator
from .validators import validate_slug

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
        








