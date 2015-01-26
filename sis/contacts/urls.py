# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from contacts.views import ContactListView,  ContactCreateView, ContactUpdateView
from contacts.views import OrganizationListView, OrganizationCreateView, OrganizationUpdateView, TestCreateView

urlpatterns = patterns('contacts.views',
    url(
        regex=r'^$',
        view=ContactListView.as_view(),
        name='contact_list'
    ),  
    url(
        regex=r'^create/$',
        view=ContactCreateView.as_view(),
        name='contact_create'
    ),
    url(
        regex=r'^update/(?P<pk>\d+)$',
        view=ContactUpdateView.as_view(),
        name='contact_update'
    ),
    url(
        regex=r'^org/$',
        view=OrganizationListView.as_view(),
        name='org_list'
    ),                  
    url(
        regex=r'^org/create/$',
        view=OrganizationCreateView.as_view(),
        name='org_create'
    ),
                       url(
        regex=r'^test/create/$',
        view=TestCreateView.as_view(),
        name='test_create'
    ),
    url(
        regex=r'^org/update/(?P<pk>\d+)$',
        view=OrganizationUpdateView.as_view(),
        name='org_update'
    ),

)
