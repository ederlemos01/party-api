from rest_framework import generics
from .serializers import CreateTicketTypeSerializer,RetrieveTicketTypeSerializer,ListMyTicketsSerializer
from events.permissions import IsEventManager
from organizations.permissions import IsOrganizationManager
from rest_framework.permissions import AllowAny
from .models import TicketType,Ticket
from events.models import Event
from django.shortcuts import get_object_or_404

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
        

class RetrieveTicketTypeView(generics.RetrieveAPIView):
    serializer_class = RetrieveTicketTypeSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    lookup_url_kwarg = 'ticket_id'

    def get_queryset(self):
        return TicketType.objects.filter(
            event__slug=self.kwargs['event_slug'],
            event__organization__slug=self.kwargs['org_slug'],
        )


class ListTicketTypeView(generics.ListAPIView):
    serializer_class = RetrieveTicketTypeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return TicketType.objects.filter(
            event__slug=self.kwargs['event_slug'],
            event__organization__slug=self.kwargs['org_slug'],
        )


class ListMyTicketsView(generics.ListAPIView):
    serializer_class = ListMyTicketsSerializer

    def get_queryset(self):
            return Ticket.objects.filter(
            holder = self.request.user
            ).select_related('ticket_type','ticket_type__event')


#a edicao e delecao do tickettype vai depender do status do eventos
    
#validacao de coisas como ticket sales tem que obedecer tambem a data de comeco do evento
