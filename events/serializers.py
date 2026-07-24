from rest_framework import serializers
from .validators import validate_slug
from .models import Event, EventStatus
from organizations.models import Organization, OrganizationRoles


class CreateEventSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(min_length = 2,validators=[validate_slug],)
    
    class Meta():
        model = Event
        fields = ['id','title','description','banner','start_at','end_at','location','slug','organization','status']
        read_only_fields = ['id']
    
    def validate_status(self, value):
        if value not in [EventStatus.DRAFT, EventStatus.PUBLISHED]:
            raise serializers.ValidationError(
                "esse nao eh um statu valido para a criacao"
            )
        return value
        
    def validate(self, attrs):
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')
        if start_at and end_at and start_at >= end_at:
            raise serializers.ValidationError({
                "end_at": "A data de término deve ser estritamente posterior à data de início."
            })
        
        
        request = self.context.get('request')
        user = request.user
        
        organization = attrs.get('organization')
        slug = attrs.get('slug')

        is_manager = user.org_memberships.filter(organization = organization,role = OrganizationRoles.MANAGER).exists()
        is_owner = user.owned_organizations.filter(id=organization.id).exists()
        if not (is_manager or is_owner):
            raise serializers.ValidationError({
                                "organization": "voce nao tem permissao para criar evento nessa organizacao"
                            })

        
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



class OrganizationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'photo']


class EventListSerializer(serializers.ModelSerializer):
    organization = OrganizationSummarySerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['title', 'slug', 'banner', 'start_at', 'location', 'organization']