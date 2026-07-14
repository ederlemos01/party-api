from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer, UserPerfilSerializer, UserEditPerfilSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class UserPerfilView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active = True)
    serializer_class = UserPerfilSerializer


class UserEditPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = UserEditPerfilSerializer
    def get_object(self):
        return self.request.user
    
