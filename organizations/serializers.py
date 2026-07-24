from rest_framework import serializers
from .models import OrganizationMember,Organization,OrganizationRoles, OrganizationInvite
from rest_framework.validators import UniqueValidator
from .validators import validate_slug
class OrganizationMemberSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrganizationMember
        fields = ['user','role']
        read_only_fields = ['user','role']

    
class EditOrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = ['id', 'role', 'user']
        read_only_fields = ['id', 'user']

    def validate_role(self, value):

        if value == OrganizationRoles.OWNER:
            raise serializers.ValidationError("Apenas o sistema pode gerar esse cargo.")
        return value
    

class OutputInviteOrganizationMemberSerializer(serializers.ModelSerializer):
    invited_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = OrganizationInvite
        fields = ['id', 'invited_by', 'user','organization', 'role']
        read_only_fields = ['id','organization','user','role','invited_by']


class OrganizationEditProfileSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(min_length=2,
        validators=[
            UniqueValidator(
                queryset=Organization.objects.all(),
                lookup='iexact', 
                message="Esse link já está sendo usado por outro Organizador. Escolha outro!"
            ), validate_slug
        ]
    )



    class Meta:
        model = Organization
        fields = ['name','description','photo','banner','slug']
        


class OrganizationPerfilSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id','name','description','photo','banner','slug']
        read_only_fields = ['id','name','description','photo','banner','slug']

class OrganizationCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Organization
        fields = ['id','slug']
        read_only_fields = ['id','slug']

    def validate(self, attrs):
        request = self.context.get('request')
        
        if request.user.owned_organizations.exists():
            raise serializers.ValidationError({
                "organization": "voce ja possui uma organizacao"
            })
        
        return super().validate(attrs)
    

class InviteMemberInputSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = OrganizationInvite
        fields = ['role','email']

    def validate_role(self, value):
        if value == OrganizationRoles.OWNER:
            raise serializers.ValidationError("Apenas o sistema pode gerar esse cargo.")
        return value
        









