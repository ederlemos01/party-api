from django.urls import path
from . import views 

urlpatterns = [
    path('',views.CreateEventView.as_view(), name='create-event'),
    path('<slug:event_slug>/', views.EventEditView.as_view(), name='edit-event'),
    path('<slug:event_slug>/invites/', views.InviteEventMemberView.as_view(), name='invite-event-members'),
]