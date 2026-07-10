from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrganizationFollowSerializer,OrganizationPerfilSerializer
from .models import OrganizationFollow, Organization
from rest_framework import generics
from django.db import IntegrityError

class FollowOrganizationView(generics.GenericAPIView):
    serializer_class = OrganizationFollowSerializer 
    queryset = Organization.objects.all()
    def post(self, request,org_slug,format=None):
        organization = get_object_or_404(self.get_queryset(), slug=org_slug)
        if OrganizationFollow.objects.filter(user=request.user, organization=organization).exists():
            return Response(
                {"detail": "Você já segue esta organização."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try: 
            my_follow = OrganizationFollow.all_objects.dead().get(
                user=request.user, 
                organization=organization
            )
            my_follow.restore()
            serializer = OrganizationFollowSerializer(my_follow)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except OrganizationFollow.DoesNotExist:
            serializer = OrganizationFollowSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            try:
                serializer.save(organization = organization)
            except IntegrityError:
                return Response(
                {"detail": "Você já segue esta organização."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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








    




    