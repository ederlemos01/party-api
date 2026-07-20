from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, exceptions
from .serializers import OrganizationPerfilSerializer,OrganizationEditProfileSerializer, OrganizationCreateSerializer,OrganizationMemberSerializer, EditOrganizationMemberSerializer, InviteMemberInputSerializer, OutputInviteOrganizationMemberSerializer
from .models import OrganizationFollow, Organization, OrganizationMember, Roles,  OrganizationInvite
from rest_framework import generics,serializers
from django.db import IntegrityError, transaction
from .permissions import IsManager, IsOwner
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from .services import invite_member
authuser = get_user_model()

class FollowOrganizationView(generics.GenericAPIView):
    queryset = Organization.objects.all()
    
    @extend_schema(request=None, responses={201: None})
    def post(self, request,org_slug,format=None):
        org = get_object_or_404(self.get_queryset(), slug=org_slug)
        OrganizationFollow.all_objects.update_or_create(user=request.user, organization=org, defaults={'deleted_at': None})
        return Response(status=status.HTTP_201_CREATED)
    
    @extend_schema(request=None, responses={204: None})
    def delete(self,request,org_slug,format=None):
        organization = get_object_or_404(self.get_queryset(), slug=org_slug)
        follow = get_object_or_404(OrganizationFollow, user=request.user, organization=organization)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class OrganizationProfile(generics.RetrieveAPIView):
    serializer_class = OrganizationPerfilSerializer
    permission_classes = [AllowAny]
    queryset = Organization.objects.all()
    lookup_field = 'slug'          
    lookup_url_kwarg = 'org_slug'

class CreateOrganizationView(generics.CreateAPIView):
    serializer_class = OrganizationCreateSerializer

    @transaction.atomic 
    def perform_create(self, serializer):
        try:
            new_organization = serializer.save(owner = self.request.user)
        except IntegrityError:
            raise serializers.ValidationError({"organization": "voce ja possui uma organizacao"})
        
        OrganizationMember.objects.create(
            user=self.request.user,
            organization=new_organization,
            role=Roles.OWNER) 



class EditOrganizationProfileView(generics.UpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationEditProfileSerializer
    permission_classes = [IsManager]
    lookup_field = 'slug'          
    lookup_url_kwarg = 'org_slug'


class ListOrganizationMembersView(generics.ListAPIView):
    permission_classes = [IsOwner]
    serializer_class = OrganizationMemberSerializer

    def get_queryset(self):
        org_slug = self.kwargs.get('org_slug')
        return OrganizationMember.objects.filter(organization__slug=org_slug)
    

class ManageOrganizationMembersView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwner]
    serializer_class = EditOrganizationMemberSerializer
    
    def get_queryset(self):
        org_slug = self.kwargs.get('org_slug')
        return OrganizationMember.objects.filter(organization__slug=org_slug,organization__deleted_at__isnull=True)

    def perform_update(self, serializer):
        member = serializer.instance 
        
        if member.user == self.request.user:
            raise exceptions.PermissionDenied("voce nao pode editar seu propio cargo.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            raise exceptions.PermissionDenied("voce nao pode deletar seu propio cargo.")
        instance.delete()
    



class InviteOrganizationMemberView(generics.GenericAPIView):
    permission_classes = [IsOwner]
    serializer_class = InviteMemberInputSerializer
    
    @extend_schema(responses={201: OutputInviteOrganizationMemberSerializer})
    def  post(self,request, org_slug):
        org = get_object_or_404(Organization, slug=org_slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invite = invite_member(email=serializer.validated_data["email"],invited_by=request.user,
                    role=serializer.validated_data["role"], org=org)
   
        return Response(
            OutputInviteOrganizationMemberSerializer(invite).data,
            status=status.HTTP_201_CREATED,
        )


class AcceptOrganizationInviteView(generics.GenericAPIView):
    
    @extend_schema(request=None, responses={201: OrganizationMemberSerializer})
    def post(self, request, invite_pk):
        invite = get_object_or_404(OrganizationInvite, id=invite_pk)
        with transaction.atomic():
            member = invite.accept(by_user=request.user)
        return Response(OrganizationMemberSerializer(member).data, status=201)








    




    