from rest_framework import serializers
from django.contrib.auth import password_validation
from rest_framework.validators import UniqueValidator


from .validators import username_validator
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup='iexact',
                message='Ja existe um usuario com este email.',
            ),
        ],
        max_length=254
        
    )
    username = serializers.CharField(
        max_length=15,
        validators=[
            username_validator,
            UniqueValidator(
                queryset=User.objects.all(),
                lookup='iexact',
                message='Este username ja esta em uso.',
            ),
        ],
    )
    
    
    
    
    
    
    
    class Meta:
        model = User
        fields = ['email','username','password']
        extra_kwargs = {'password': {'write_only': True}}



    def validate_password(self, value):
        user = User(
            email=self.initial_data.get('email', ''),
            username=self.initial_data.get('username', ''),
            )
        password_validation.validate_password(value, user=user)
        return value
        
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)