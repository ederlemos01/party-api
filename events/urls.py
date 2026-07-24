from django.urls import path
from . import views 

urlpatterns = [
    path('',views.CreateEventView.as_view(), name='create-event'),
    path('<slug:org_slug>/<slug:event_slug>/',views.EventPerfilView.as_view(), name='event-perfil'),
    path('home/',views.EventListView.as_view(), name='home')
]