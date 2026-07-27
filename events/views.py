from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CreateEventSerializer, EventPerfilSerializer, EventListSerializer, EditEventSerializer,EventMemberSerializer, InviteMemberInputSerializer,InviteMemberOutputSerializer
from rest_framework.permissions import AllowAny
from .models import Event, EventStatus, EventMember, EventRoles,EventInvite
from django.utils import timezone
from organizations.permissions import IsOwner, IsOrganizationManager
from django.db import transaction, IntegrityError
from rest_framework import serializers
from .permissions import IsEventManager
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from .services import invite_member


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

class EventEditView(generics.UpdateAPIView):
    serializer_class = EditEventSerializer
    permission_classes = [IsOrganizationManager|IsEventManager]
    lookup_field = 'slug'
    lookup_url_kwarg = 'event_slug'

    def get_queryset(self):
            return Event.objects.filter(organization__slug = self.kwargs['org_slug'],
                                         organization__deleted_at__isnull = True,
                                         )
    def perform_update(self, serializer):
                try:
                    with transaction.atomic():
                        serializer.save()
                except IntegrityError:
                    raise serializers.ValidationError({"slug": "já existe um evento com esse slug nessa organização"})


class InviteEventMemberView(generics.GenericAPIView):
    permission_classes = [IsEventManager]
    serializer_class = InviteMemberInputSerializer
    
    @extend_schema(responses={201: InviteMemberOutputSerializer})
    def  post(self,request, event_slug, org_slug):
        event = get_object_or_404(Event, slug=event_slug, organization__slug = org_slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invite = invite_member(email=serializer.validated_data["email"],invited_by=request.user,
                    role=serializer.validated_data["role"], event=event)
   
        return Response(
            InviteMemberOutputSerializer(invite).data,
            status=status.HTTP_201_CREATED,
        )


class AcceptEventInviteView(generics.GenericAPIView):
    
    @extend_schema(request=None, responses={201: EventMemberSerializer})
    def post(self, request, invite_pk):
        invite = get_object_or_404(EventInvite, id=invite_pk)
        with transaction.atomic():
            member = invite.accept(by_user=request.user)
        return Response(EventMemberSerializer(member).data, status=201)
