from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

# rest_framework imports
from rest_framework.routers import SimpleRouter

from viewsets import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'samplingcontrol.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^login/', 'rest_framework_jwt.views.obtain_jwt_token',  name='api-login'),       
    url(r'^docs/', include('rest_framework_swagger.urls'),        name='api-docs'),
    
    url(r'^admin/$', AdminListViewset.as_view(),                  name='api-admin'),
    url(r'^admin/(?P<pk>[0-9]+)/$', AdminDetailViewset.as_view(), name='api-admin-detail'),
    
    url(r'^eventuser/$',                     EventUserListViewset.as_view(),     name='api-event-user'),
    url(r'^eventuser/(?P<pk>[0-9]+)/$',      EventUserDetailViewset.as_view(),   name='api-event-user-detail'),
    url(r'^eventuser/edit/$',                EventUserEditListViewset.as_view(), name='api-event-user-edit'),
    url(r'^eventuser/edit/(?P<pk>[0-9]+)/$', EventUserEditViewset.as_view(),     name='api-event-user-edit-pk'),
            
    url(r'^admin/checkname/$', CheckAdminNameViewset.as_view({'post': 'checkname'}), name='api-admin-check-name'),
    
    url(r'^event/multidelete/$', EventMultiDeleteViewset.as_view({'post': 'multidelete'}), name='api-event-multidelete'),
    url(r'^event/graph/(?P<pk>[0-9]+)/$',   TrackDataGraphViewset.as_view({'get': 'generate_graph_data'}), name='api-trackdata-graph'),

    
    

]

# Add routers for REST endpoints
router = SimpleRouter()
router.register(r'event', EventViewset,'api-event')
urlpatterns += router.urls

