from django.urls import path
from . import views 

urlpatterns = [
     path('', views.CreateTicketTypeView.as_view(), name='create-tickettype'),
]