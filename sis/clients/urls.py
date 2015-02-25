# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from clients.views import ClientListView,  ClientCreateView, ClientSetupView
from clients.views import ClientProfileIdentificationView, ClientProfileContactView, ClientProfileCommunicationView, ClientProfileReferralView, ClientProfileRelationshipView, ClientProfileOrderView, ClientProfileDietView
from clients.views import ClientProfileEditIdentificationView, ClientProfileEditContactView, ClientProfileEditCommunicationView, ClientProfileEditReferralView, ClientProfileEditOrderView
from clients.views import ClientRelationshipListView, RelationshipCreateView, RelationshipEditView, RelationshipDeleteView


urlpatterns = patterns('clients.views',
    url(
        regex=r'^$',
        view=ClientListView.as_view(),
        name='client_list'
    ),
    
    url(
        regex=r'^create/$',
        view=ClientCreateView.as_view(),
        name='client_create'
    ),
    
    url(
        regex=r'^setup/(?P<pk>\d+)$',
        view=ClientSetupView.as_view(),
        name='client_setup'
    ),
    url(
        regex=r'^setup/resume/(?P<pk>\d+)$',
        view=ClientSetupView.as_view(),
        name='client_setup_resumeo'
    ),
    url(
        regex=r'^profile/id/(?P<pk>\d+)$',
        view=ClientProfileIdentificationView.as_view(),
        name='client_profile_identification'
    ),
    url(
        regex=r'^profile/contact/(?P<pk>\d+)$',
        view=ClientProfileContactView.as_view(),
        name='client_profile_contact'
    ), 
    url(
        regex=r'^profile/comm/(?P<pk>\d+)$',
        view=ClientProfileCommunicationView.as_view(),
        name='client_profile_communication'
    ),
    url(
        regex=r'^profile/ref/(?P<pk>\d+)$',
        view=ClientProfileReferralView.as_view(),
        name='client_profile_referral'
    ),
    url(
        regex=r'^profile/rel/(?P<pk>\d+)$',
        view=ClientProfileRelationshipView.as_view(),
        name='client_profile_relationship'
    ),
    url(
        regex=r'^(?P<pk>\d+)/rel$',
        view=ClientRelationshipListView.as_view(),
        name='client_relationship_list'
    ),
    url(
        regex=r'^profile/order/(?P<pk>\d+)$',
        view=ClientProfileOrderView.as_view(),
        name='client_profile_order'
    ),
    url(
        regex=r'^profile/diet/(?P<pk>\d+)$',
        view=ClientProfileDietView.as_view(),
        name='client_profile_diet'
    ),
    url(
        regex=r'^rel/(?P<pk>\d+)/create$', # pk of client
        view=RelationshipCreateView.as_view(),
        name='relationship_create'
    ),                   
    url(
        regex=r'^rel/(?P<pk>\d+)/edit$', # pk of relationship
        view=RelationshipEditView.as_view(),
        name='relationship_edit'
    ), 
    url(
        regex=r'^rel/(?P<pk>\d+)/delete$', # pk of relationship
        view=RelationshipDeleteView.as_view(),
        name='relationship_delete'
    ),                
    url(
        regex=r'^profile/id/(?P<pk>\d+)/edit$',
        view=ClientProfileEditIdentificationView.as_view(),
        name='client_profile_identification_edit'
    ), 
    url(
        regex=r'^profile/contact/(?P<pk>\d+)/edit$',
        view=ClientProfileEditContactView.as_view(),
        name='client_profile_contact_edit'
    ), 
    url(
        regex=r'^profile/comm/(?P<pk>\d+)/edit$',
        view=ClientProfileEditCommunicationView.as_view(),
        name='client_profile_communication_edit'
    ), 
    url(
        regex=r'^profile/ref/(?P<pk>\d+)/edit$',
        view=ClientProfileEditReferralView.as_view(),
        name='client_profile_referral_edit'
    ), 
    url(
        regex=r'^profile/order/(?P<pk>\d+)/edit$',
        view=ClientProfileEditOrderView.as_view(),
        name='client_profile_order_edit'
    )   
             

)
