from django.urls import path
from . import views 

urlpatterns = [
    path('',views.CreateEventView.as_view(), name='create-event'),
    path('<slug:org>/<slug:event>/',views.EventPerfilView.as_view(), name='event-perfil')
]