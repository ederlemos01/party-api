from rest_framework import generics, serializers
from .serializers import CreateEventSerializer, EventPerfilSerializer, EventListSerializer
from rest_framework.permissions import AllowAny
from .models import Event, EventStatus
from django.db import IntegrityError
from django.utils import timezone

class CreateEventView(generics.CreateAPIView):
    serializer_class = CreateEventSerializer
        

class EventPerfilView(generics.RetrieveAPIView):
    serializer_class = EventPerfilSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    lookup_url_kwarg = 'event_slug'
    
    def get_queryset(self):
        return Event.objects.filter(organization__slug = self.kwargs['org_slug'],
                                     organization__deleted_at__isnull = True,
                                     status=EventStatus.PUBLISHED)

    
class EventListView(generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Event.objects
            .filter(
                status=EventStatus.PUBLISHED,
                organization__deleted_at__isnull=True,
                end_at__gte=timezone.now(),
            )
            .select_related('organization')
            .order_by('start_at')
        )
    
