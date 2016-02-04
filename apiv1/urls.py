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
    
           
    url(r'^$', RedirectView.as_view(url='/api/v1/docs/',),        name='api-docs'),
    url(r'^docs/', include('rest_framework_swagger.urls'),        name='api-docs'),
    

    
    ############################
    # Backend endpoints - v1
    ############################
    
    # Returns the task for the user
    url(r'^task/$', TaskViewset.as_view({'post': 'post'}), name='api-task'),
    
    url(r'^login/', LoginAppViewset.as_view({'post': 'post'}),  name='api-dfs-login'),
    
    # Track    
    url(r'^trackdata/checkin/$', EventCheckinViewset.as_view({'post': 'post'}), name='api-task'),
    url(r'^trackdata/checkout/$', EventCheckoutViewset.as_view({'post': 'post'}), name='api-task'),
    url(r'^trackdata/report/$', TrackDataViewset.as_view({'post': 'post'}), name='api-task'),
]



