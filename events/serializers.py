from rest_framework import serializers
from .validators import validate_slug
from .models import Event, EventStatus,EventMember,EventInvite
from organizations.models import Organization
from django.shortcuts import get_object_or_404
from .services import validate_event



class EventMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'start_at', 'location']
        
class CreateEventSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(min_length = 2,validators=[validate_slug],)
    
    class Meta():
        model = Event
        fields = ['id','title','description','banner','start_at','end_at','location','slug','organization','status']
        read_only_fields = ['id','organization','status']
        
    def validate(self, attrs):
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')
        org_slug = self.context['view'].kwargs.get('org_slug')
        organization = get_object_or_404(Organization, slug=org_slug, deleted_at__isnull=True)
        slug = attrs.get('slug')

        validate_event(start_at=start_at,end_at=end_at,organization=organization,slug=slug)

        attrs['organization'] = organization
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

class EditEventSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(min_length = 2,validators=[validate_slug],)
        
    class Meta():
        model = Event
        fields = ['id','title','description','banner','start_at','end_at','location','slug','status']
        read_only_fields = ['id']

    def validate_status(self,value):
        if value not in [EventStatus.DRAFT, EventStatus.PUBLISHED, EventStatus.CANCELED]:
            raise serializers.ValidationError({
                            "status": "esse status nao e valido para o evento"
                        })
        return value

    def validate(self, attrs):
        start_at = attrs.get('start_at', self.instance.start_at)
        end_at   = attrs.get('end_at',   self.instance.end_at)
        organization = self.instance.organization
        slug = attrs.get('slug')

        validate_event(start_at=start_at,end_at=end_at,organization=organization,slug=slug, instance=self.instance)

        return super().validate(attrs)


class EventMemberSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EventMember
        fields = ['user','role']
        read_only_fields = ['user','role']


class InviteMemberInputSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = EventInvite
        fields = ['role','email']


class InviteMemberOutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventInvite
        fields = ['id', 'invited_by', 'user','event', 'role']
        read_only_fields = ['id','event','user','role','invited_by']