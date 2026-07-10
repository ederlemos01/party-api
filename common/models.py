import uuid

from django.db import models
from django.utils import timezone

#essa classe aplica soft delete em todos metodos que mexem com query, model.objects.filter().delete()
class SoftDeleteQuerySet(models.QuerySet):
 
    def delete(self):
        return self.update(deleted_at=timezone.now(), updated_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def restore(self):
        return self.update(deleted_at=None, updated_at=timezone.now())

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def alive(self):
        return self.filter(deleted_at__isnull=True)

#essa classe aplica soft delete em todos metodos que mexem com o manager individual, model.objects.delete()
class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

#rescrevemos o metodo delete, model.delete()
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True
        base_manager_name = 'all_objects'
        ordering = ['-created_at']

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at', 'updated_at'])
