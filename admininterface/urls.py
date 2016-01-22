from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from views import *

urlpatterns = [
    url(r'^$',          TemplateView.as_view(template_name='sample.html'),      name='root'),
    
    url(r'^login/$',     LoginView.as_view(),        name='login'),
    url(r'^logout/$',    LogoutView.as_view(),        name='logout'),
    
    
    url(r'^base/$',            BaseView.as_view(template_name='base.html'),        name='base'),
    url(r'^home/$',            BaseView.as_view(template_name='home/eventresult.html'),   name='home'),
    url(r'^home/analysis/0/$', BaseView.as_view(template_name='home/eventtable.html'),    name='analysis'),
    
    url(r'^events/$',             BaseView.as_view(template_name='manage/events.html'),    name='events'),
    url(r'^addevent/$',           BaseView.as_view(template_name='base.html'),    name='add_event'),
    url(r'^editevent/$',          BaseView.as_view(template_name='base.html'),    name='edit_event'),    
    url(r'^event/events/0/$',     BaseView.as_view(template_name='manage/events.html'),    name='events_0'),
    
    url(r'^admin/$',             BaseView.as_view(template_name='base.html'),    name='admins'),
    url(r'^users/$',              BaseView.as_view(template_name='manage/users.html'),    name='users'),
    url(r'^admin/admins/0/$',     BaseView.as_view(template_name='manage/admins.html'),    name='admin_0'),
    url(r'^manage/users/0/$',     BaseView.as_view(template_name='manage/users.html'),    name='users_0'),
    
    
    url(r'^settings/changepwd/$', BaseView.as_view(template_name='settings/changepwd.html'),    name='changepwd'),    
    
]
