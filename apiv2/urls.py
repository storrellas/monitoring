from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse

# rest_framework imports
from rest_framework.routers import SimpleRouter

from viewsets import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'samplingcontrol.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
           
    url(r'^$', RedirectView.as_view(url='/api/v2/docs/',),        name='api-docs'),
    url(r'^docs/', include('rest_framework_swagger.urls'),        name='api-docs'),
    
    
    url(r'^login/',                               LoginAppViewset.as_view({'post': 'post'}),   name='api-v2-login'),
    url(r'^event/$',                              EventListAppViewset.as_view(),         name='api-v2-event-list'),
    url(r'^event/(?P<pk>[0-9]+)/$',               EventDetailAppViewset.as_view(),             name='api-v2-event-detail'),
    url(r'^eventcheck/$',                         EventCheckAppViewset.as_view(),            name='api-v2-eventcheck'),
    url(r'^eventcheck/checkin/$',                 EventCheckInAppViewset.as_view(),            name='api-v2-eventcheck-in'),
    url(r'^eventcheck/checkout/(?P<pk>[0-9]+)/$', EventCheckOutAppViewset.as_view(),           name='api-v2-eventcheck-out'),
    url(r'^eventcheck/report/(?P<pk>[0-9]+)/$',   EventCheckReportAppViewset.as_view(),        name='api-v2-report'),

    
    url(r'^eventcheck/photo/(?P<pk>[0-9]+)/$',    EventCheckPhotoAppViewset.as_view({'post': 'post'}), name='api-v2-report'),
]



