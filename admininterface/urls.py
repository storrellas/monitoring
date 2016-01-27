from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView,RedirectView
from views import *

urlpatterns = [
    #url(r'^test/$',          TemplateView.as_view(template_name='sample.html'),      name='root'),
    url(r'^$',                RedirectView.as_view(url='/home/'),      name='root'),
    
    url(r'^login/$',          LoginView.as_view(),        name='login'),
    url(r'^logout/$',         LogoutView.as_view(),        name='logout'),
    
    
    url(r'^base/$',            BaseView.as_view(template_name='base.html'),        name='base'),
    url(r'^home/$',            BaseView.as_view(template_name='home/eventresult.html'),   name='home'),
    url(r'^home/analysis/0/$', BaseView.as_view(template_name='home/eventtable.html'),    name='analysis'),
    

        
    url(r'^event/events/0/$',     EventView.as_view(),    name='events_0'),
    url(r'^event/add/$',           BaseView.as_view(template_name='manage/addevent.html'),    name='add_event'),
    url(r'^event/edit/(?P<pk>[0-9]+)/$',          BaseView.as_view(template_name='manage/editevent.html'),    name='edit_event'),
    
    url(r'^admin/$',              BaseView.as_view(template_name='base.html'),    name='admin'),
    url(r'^users/$',              BaseView.as_view(template_name='manage/users.html'),    name='users'),
    url(r'^admin/admins/(?P<admin_id>[0-9]+)/$',    AdminView.as_view(),    name='admin_0'),
    url(r'^manage/users/(?P<user_id>[0-9]+)/$',     EventUserView.as_view(),    name='users_0'),
    
    
    url(r'^settings/changepwd/$', BaseView.as_view(template_name='settings/changepwd.html'),    name='changepwd'),    
    
]
