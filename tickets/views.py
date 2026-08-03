from rest_framework import generics
from .serializers import CreateTicketTypeSerializer,RetrieveTicketTypeSerializer
from events.permissions import IsEventManager
from organizations.permissions import IsOrganizationManager
from rest_framework.permissions import AllowAny
from .models import TicketType
from events.models import Event
from django.shortcuts import get_object_or_404
from django.db import transaction

class CreateTicketTypeView(generics.CreateAPIView):
    serializer_class = CreateTicketTypeSerializer
    permission_classes = [IsEventManager | IsOrganizationManager]

    def perform_create(self, serializer):
        org_slug = self.kwargs.get('org_slug')
        event_slug = self.kwargs.get('event_slug')
        event = get_object_or_404(
                Event, 
                slug=event_slug, 
                organization__slug=org_slug 
            )
        serializer.save(event=event)
        

class ShowTicketTypeView(generics.RetrieveAPIView):
    serializer_class = RetrieveTicketTypeSerializer
    permission_classes = [AllowAny]
    queryset = TicketType.objects.all()
    lookup_field = 'uuid'          
    lookup_url_kwarg = 'ticket_id'




#a edicao e delecao do tickettype vai depender do status do eventos
    
#validacao de coisas como ticket sales tem que obedecer tambem a data de comeco do evento
