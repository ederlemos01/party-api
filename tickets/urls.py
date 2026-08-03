from django.urls import path
from . import views 

urlpatterns = [
     path('<uuid:ticket_id>/', views.ShowTicketTypeView.as_view(), name='show-tickettype')
]