from django.urls import path
from . import views

urlpatterns = [
    
     path('<uuid:ticket_id>/', views.RetrieveTicketTypeView.as_view(), name='retrieve-tickettype'),
     path('', views.ListTicketTypeView.as_view(), name='list-tickettype')
]