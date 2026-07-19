from django.urls import path
from . import views 

urlpatterns = [
    path('<slug:org_slug>/followers/', views.FollowOrganizationView.as_view(), name='organization-follow'),
    path('<slug:org_slug>/', views.OrganizationProfile.as_view(), name='organization-profile'),
    path('invites/<uuid:invite_pk>/accept/', views.AcceptOrganizationInviteView.as_view(), name='accept-organization-invite')  
]