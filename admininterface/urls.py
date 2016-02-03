from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required


# rest_framework imports
from rest_framework.routers import SimpleRouter

from django.views.generic import TemplateView,RedirectView
from views import *
from viewsets import *

urlpatterns = [
    #url(r'^test/$',          TemplateView.as_view(template_name='sample.html'),      name='root'),
    url(r'^$',                    RedirectView.as_view(url='/home/'),      name='root'),
    
    url(r'^login/$',              LoginView.as_view(),        name='login'),
    url(r'^logout/$',             LogoutView.as_view(),        name='logout'),
    
    
    url(r'^base/$',                BaseView.as_view(template_name='base.html'),        name='base'),
    url(r'^home/$',                EventResultView.as_view(template_name='home/event_result.html'),   name='home'),
    url(r'^home/analysis/$',       EventAnalysisView.as_view(),    name='event_analysis'),
    url(r'^home/analysis/csv/$',   EventAnalysisCSVView.as_view(),    name='event_analysis_csv'),
        
    url(r'^event/$',                        EventView.as_view(),    name='event'),
    url(r'^event/add/$',                    EventAddView.as_view(),    name='add_event'),
    url(r'^event/edit/(?P<pk>[0-9]+)/$',    EventEditView.as_view(template_name='manage/editevent.html'),    name='edit_event'),
    
    url(r'^admin/$',              BaseView.as_view(template_name='base.html'),    name='admin'),
    url(r'^users/$',              BaseView.as_view(template_name='manage/users.html'),    name='users'),
    url(r'^admin/admins/(?P<admin_id>[0-9]+)/$',    AdminView.as_view(),    name='admin_0'),
    url(r'^manage/users/(?P<user_id>[0-9]+)/$',     EventUserView.as_view(),    name='users_0'),
    
    
    url(r'^settings/changepwd/$', BaseView.as_view(template_name='settings/changepwd.html'),    name='changepwd'),    
    
    ############
    # AJAX enpoints
    ############
    url(r'^ajax/login/',                  'rest_framework_jwt.views.obtain_jwt_token',  name='ajax-login'),
    url(r'^ajax/admin/$',                  AdminListViewset.as_view(),                  name='ajax-admin'),
    url(r'^ajax/admin/(?P<pk>[0-9]+)/$',   AdminDetailViewset.as_view(),                name='ajax-admin-detail'),
    
    url(r'^ajax/eventuser/$',              EventUserListViewset.as_view(),              name='ajax-event-user'),
    

    
    url(r'^ajax/eventuser/(?P<pk>[0-9]+)/$',      EventUserDetailViewset.as_view(),   name='ajax-event-user-detail'),
    url(r'^ajax/eventuser/edit/$',                EventUserEditListViewset.as_view(), name='ajax-event-user-edit'),
    url(r'^ajax/eventuser/edit/(?P<pk>[0-9]+)/$', EventUserEditViewset.as_view(),     name='ajax-event-user-edit-pk'),
            
    url(r'^ajax/admin/checkname/$',               CheckAdminNameViewset.as_view({'post': 'checkname'}), name='ajax-admin-check-name'),
    
    url(r'^ajax/event/multidelete/$',             EventMultiDeleteViewset.as_view({'post': 'multidelete'}), name='ajax-event-multidelete'),
    url(r'^ajax/event/graph/(?P<pk>[0-9]+)/$',    TrackDataGraphViewset.as_view({'get': 'generate_graph_data'}), name='ajax-trackdata-graph'),
    
]

# Add routers for REST endpoints
router = SimpleRouter()
router.register(r'ajax/event', EventViewset,'api-event')
urlpatterns += router.urls
