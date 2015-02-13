# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from clients.views import ClientListView,  ClientCreateView, ClientSetupView, ClientUpdateView, ClientProfileView, ClientReferralView, ClientOrderView
from clients.views import ClientProfileIdentificationView, ClientProfileContactView, ClientProfileCommunicationView, ClientProfileReferralView
from clients.views import ClientProfileEditIdentificationView, ClientProfileEditContactView, ClientProfileEditCommunicationView, ClientProfileEditReferralView


urlpatterns = patterns('clients.views',
    url(
        regex=r'^$',
        view=ClientListView.as_view(),
        name='client_list'
    ),
#     url(
#         regex=r'^clients_data_110$',
#         view=ClientListViewJson.as_view(),
#         name='client_list_json'
#     ),
    
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
        regex=r'^profile/(?P<tab>\w+)/(?P<pk>\d+)$',
        view=ClientProfileView.as_view(),
        name='client_profile_o'
    ),
    url(
        regex=r'^profile/(?P<pk>\d+)/referral$',
        view=ClientReferralView.as_view(),
        name='client_profile_referral_o'
    ),
    url(
        regex=r'^profile/(?P<pk>\d+)/order$',
        view=ClientOrderView.as_view(),
        name='client_profile_order_o'
    ),
    url(
        regex=r'^update/(?P<pk>\d+)$',
        view=ClientUpdateView.as_view(),
        name='client_update'
    ),
                       

)
