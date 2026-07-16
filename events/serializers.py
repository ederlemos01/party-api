from rest_framework import serializers
from .validators import validate_slug
from .models import Event

class CreateEventSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(min_length = 2,validators=[validate_slug],)
    class Meta():
        model = Event
        fields = ['id','title','description','banner','start_at','end_at','location','slug','organization']
        read_only_fields = ['id','organization']
    
    def validate(self, attrs):
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')

        if start_at and end_at and start_at >= end_at:
            raise serializers.ValidationError({
                "end_at": "A data de término deve ser estritamente posterior à data de início."
            })
        
        
        request = self.context.get('request')
    
        organization = request.user.owned_organizations.first()
        
        if not organization:
            raise serializers.ValidationError("Você precisa criar uma organização antes de criar eventos.")

        slug = attrs.get('slug')
        
        if organization and slug:
            slug_is_taken = Event.objects.filter(
                organization=organization, 
                slug=slug, 
                deleted_at__isnull=True
            ).exists()
        
            if slug_is_taken:
                raise serializers.ValidationError({
                    "slug": "ja possui um evento com esse slug na organizacao"
                })
        return super().validate(attrs)
    


class EventPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id','title','description','banner','start_at','end_at','location','slug','organization']
        read_only_fields = ['id','title','description','banner','start_at','end_at','location','slug','organization']