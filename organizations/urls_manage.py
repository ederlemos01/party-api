from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateOrganizationView.as_view(), name='create-organization'),
    path('<slug:org_slug>/', views.EditOrganizationProfileView.as_view(), name='edit-organization-profile'),
]
