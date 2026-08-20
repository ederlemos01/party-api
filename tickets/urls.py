from django.urls import path
from . import views

urlpatterns = [

     path('<slug:org_slug>/<slug:event_slug>/<uuid:ticket_id>/', views.RetrieveTicketTypeView.as_view(), name='retrieve-tickettype'),
     path('<slug:org_slug>/<slug:event_slug>/', views.ListTicketTypeView.as_view(), name='list-tickettype'),
     path('', views.ListMyTicketsView.as_view(), name='list-my-tickets'),

]
