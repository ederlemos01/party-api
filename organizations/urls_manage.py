from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateOrganizationView.as_view(), name='create-organization'),
    path('<slug:org_slug>/', views.EditOrganizationProfileView.as_view(), name='edit-organization-profile'),
    path('<slug:org_slug>/members/', views.ListOrganizationMembersView.as_view(), name='list-organization-members'),
    path('<slug:org_slug>/members/<uuid:pk>/', views.ManageOrganizationMembersView.as_view(), name='manage-organization-members'),
    path('<slug:org_slug>/invites/', views.InviteOrganizationMemberView.as_view(), name='invite-organization-members'),
    ]
