# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from contacts.views import ContactListView,  ContactCreateView, ContactUpdateView

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

)
