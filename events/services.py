from rest_framework import serializers
from .models import Event


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