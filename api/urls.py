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
    url(r'^web/login/', 'rest_framework_jwt.views.obtain_jwt_token',  name='api-login'),       
    url(r'^$', RedirectView.as_view(url='/api/docs/',),        name='api-docs'),
    url(r'^web/docs/', include('rest_framework_swagger.urls'),        name='api-docs'),
    
    url(r'^web/admin/$', AdminListViewset.as_view(),                  name='api-admin'),
    url(r'^web/admin/(?P<pk>[0-9]+)/$', AdminDetailViewset.as_view(), name='api-admin-detail'),
    
    url(r'^web/eventuser/$',                     EventUserListViewset.as_view(),     name='api-event-user'),
    

    
    url(r'^web/eventuser/(?P<pk>[0-9]+)/$',      EventUserDetailViewset.as_view(),   name='api-event-user-detail'),
    url(r'^web/eventuser/edit/$',                EventUserEditListViewset.as_view(), name='api-event-user-edit'),
    url(r'^web/eventuser/edit/(?P<pk>[0-9]+)/$', EventUserEditViewset.as_view(),     name='api-event-user-edit-pk'),
            
    url(r'^web/admin/checkname/$', CheckAdminNameViewset.as_view({'post': 'checkname'}), name='api-admin-check-name'),
    
    url(r'^web/event/multidelete/$', EventMultiDeleteViewset.as_view({'post': 'multidelete'}), name='api-event-multidelete'),
    url(r'^web/event/graph/(?P<pk>[0-9]+)/$',   TrackDataGraphViewset.as_view({'get': 'generate_graph_data'}), name='api-trackdata-graph'),
    
    ############################3
    # Backend endpoints
    ############################3
    
    # Returns the task for the user
    url(r'^task/$', TaskViewset.as_view({'post': 'post'}), name='api-task'),
    
    url(r'^login/', LoginAppViewset.as_view({'post': 'post'}),  name='api-dfs-login'),
    
    # Track    
    url(r'^trackdata/checkin/$', EventCheckinViewset.as_view({'post': 'post'}), name='api-task'),
    url(r'^trackdata/checkout/$', EventCheckoutViewset.as_view({'post': 'post'}), name='api-task'),
    url(r'^trackdata/report/$', TrackDataViewset.as_view({'post': 'post'}), name='api-task'),
]

# Add routers for REST endpoints
router = SimpleRouter()
router.register(r'event', EventViewset,'api-event')
urlpatterns += router.urls

