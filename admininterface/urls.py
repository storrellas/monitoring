from django.conf.urls import patterns, include, url
from django.contrib import admin


# rest_framework imports
from rest_framework.routers import SimpleRouter

from django.views.generic import TemplateView,RedirectView
from views import *
from viewsets import *
from django.contrib.auth.decorators import user_passes_test

urlpatterns = [
   
    url(r'^test/$',                TemplateView.as_view(template_name='sample.html'),      name='root'),
    url(r'^$',                     RedirectView.as_view(url='/home/'),        name='root'),
    
    url(r'^login/$',               LoginView.as_view(),                name='login'),
    url(r'^logout/$',              LogoutView.as_view(),               name='logout'),
    
    url(r'^base/$',                BaseView.as_view(template_name='base.html'),        name='base'),
    url(r'^home/$',                EventAnalysisView.as_view(),        name='home'),
    url(r'^home/result/$',         EventResultView.as_view(),          name='home_results'),
    url(r'^home/result/csv/$',     EventResultCSVView.as_view(),       name='event_analysis_csv'),
        
    url(r'^event/$',               EventView.as_view(),                name='event'),
    url(r'^event/add/$',           EventAddView.as_view(),             name='add_event'),
    url(r'^event/edit/(?P<pk>[0-9]+)/$',    EventEditView.as_view(),   name='edit_event'),

    #url(r'^product/$',             TemplateView.as_view(template_name='manage/product_list.html'),  name='product'),
    url(r'^product/$',             ProductView.as_view(),  name='product'),
    
    url(r'^manage/company/$',      CompanyView.as_view(),              name='company_list'),
    url(r'^manage/users/$',        EventUserView.as_view(),            name='user_list'),
    
    
    url(r'^settings/changepwd/$',  ChangePwdView.as_view(),            name='changepwd'),    
    
    ############
    # AJAX enpoints
    ############

    url(r'^ajax/docs/',                        include('rest_framework_swagger.urls'),        name='ajax-docs'),
    url(r'^ajax/login/',                       'rest_framework_jwt.views.obtain_jwt_token',   name='ajax-login'),
    url(r'^ajax/admin/$',                      AdminListViewset.as_view(),                    name='ajax-admin'),
    url(r'^ajax/admin/(?P<pk>[0-9]+)/$',       AdminDetailViewset.as_view(),                  name='ajax-admin-detail'),
    
    url(r'^ajax/eventuser/$',                  EventUserListViewset.as_view(),                name='ajax-event-user'),
    url(r'^ajax/eventuser/(?P<pk>[0-9]+)/$',   EventUserDetailViewset.as_view(),              name='ajax-event-user-edit-pk'),

    url(r'^ajax/company/(?P<pk>[0-9]+)/event/$', CompanyUserEventViewset.as_view({'get': 'event_list'}), name='ajax-company-event'),
            
    url(r'^ajax/admin/checkname/$',            CheckAdminNameViewset.as_view({'post': 'checkname'}), name='ajax-admin-check-name'),
    
    url(r'^ajax/event/multidelete/$',          EventMultiDeleteViewset.as_view({'post': 'multidelete'}), name='ajax-event-multidelete'),
    url(r'^ajax/event/graph/(?P<pk>[0-9]+)/$', EventCheckGraphViewset.as_view({'get': 'generate_graph_data'}), name='ajax-eventcheck-graph'),

    

]


# Add routers for REST endpoints
router = SimpleRouter()
router.register(r'ajax/event',   EventViewset,'ajax-event')
router.register(r'ajax/product', ProductViewset,'ajax-product')
urlpatterns += router.urls

