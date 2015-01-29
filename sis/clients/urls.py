# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from clients.views import ClientListView,  ClientCreateView, ClientSetupView, ClientUpdateView, ClientProfileView, ClientReferralView, ClientOrderView
#ClientListViewJson,

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
        name='client_setup_resume'
    ),
    url(
        regex=r'^profile/(?P<tab>\w+)/(?P<pk>\d+)$',
        view=ClientProfileView.as_view(),
        name='client_profile'
    ),
    url(
        regex=r'^profile/(?P<pk>\d+)/referral$',
        view=ClientReferralView.as_view(),
        name='client_profile_referral'
    ),
    url(
        regex=r'^profile/(?P<pk>\d+)/order$',
        view=ClientOrderView.as_view(),
        name='client_profile_order'
    ),
    url(
        regex=r'^update/(?P<pk>\d+)$',
        view=ClientUpdateView.as_view(),
        name='client_update'
    ),
                       

)
