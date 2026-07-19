from rest_framework import generics, serializers
from .serializers import CreateEventSerializer, EventPerfilSerializer
from rest_framework.permissions import AllowAny
from .models import Event, EventStatus
from django.db import IntegrityError

class CreateEventView(generics.CreateAPIView):
    serializer_class = CreateEventSerializer
    
    def perform_create(self, serializer):
        org = self.request.user.owned_organizations.first()
        try:
            serializer.save(organization=org)
        except IntegrityError:
            raise serializers.ValidationError({"slug": "ja existe evento com esse slug na organizacao"})
        



class EventPerfilView(generics.RetrieveAPIView):
    serializer_class = EventPerfilSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    lookup_url_kwarg = 'event'
    
    def get_queryset(self):
        return Event.objects.filter(organization__slug = self.kwargs['org'],
                                     organization__deleted_at__isnull = True,
                                     status=EventStatus.PUBLISHED)
    
