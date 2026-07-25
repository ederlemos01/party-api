from django.urls import path
from . import views 

urlpatterns = [
    path('',views.CreateEventView.as_view(), name='create-event'),
]