from rest_framework import generics
from .serializers import CreateEventSerializer, EventPerfilSerializer, EventListSerializer
from rest_framework.permissions import AllowAny
from .models import Event, EventStatus, EventMember, EventRoles
from django.utils import timezone
from organizations.permissions import IsOwner, IsOrganizationManager
from django.db import transaction, IntegrityError
from rest_framework import serializers
class CreateEventView(generics.CreateAPIView):
    serializer_class = CreateEventSerializer
    permission_classes = [IsOwner |IsOrganizationManager]

    
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                event = serializer.save()
                EventMember.objects.create(user=self.request.user,event=event,role=EventRoles.MANAGER )
        except IntegrityError:
            raise serializers.ValidationError({"slug": "já existe um evento com esse slug nessa organização"})

        

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
    
