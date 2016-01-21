from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$',          TemplateView.as_view(template_name='sample.html'),      name='root'),
    
    url(r'^login/$',     TemplateView.as_view(template_name='login.html'),        name='login'),
    
    
    url(r'^base/$',     TemplateView.as_view(template_name='base.html'),        name='base'),
    url(r'^eventresult/$',     TemplateView.as_view(template_name='base.html'),   name='event_result'),
    url(r'^eventtable/$',     TemplateView.as_view(template_name='base.html'),    name='event_table'),
    url(r'^home/$',     TemplateView.as_view(template_name='base.html'),    name='home'),
    url(r'^home/analysis/0/$',     TemplateView.as_view(template_name='base.html'),    name='analysis'),
    
    url(r'^events/$',     TemplateView.as_view(template_name='base.html'),    name='events'),
    url(r'^addevent/$',     TemplateView.as_view(template_name='base.html'),    name='add_event'),
    url(r'^editevent/$',     TemplateView.as_view(template_name='base.html'),    name='edit_event'),    
    url(r'^event/events/0/$',     TemplateView.as_view(template_name='base.html'),    name='events_0'),
    
    url(r'^admins/$',     TemplateView.as_view(template_name='base.html'),    name='admins'),
    url(r'^users/$',     TemplateView.as_view(template_name='base.html'),    name='users'),
    url(r'^settings/changepwd/$',     TemplateView.as_view(template_name='base.html'),    name='changepwd'),
    url(r'^admin/admins/0/$',     TemplateView.as_view(template_name='base.html'),    name='admin_0'),
    url(r'^manage/users/0/$',     TemplateView.as_view(template_name='base.html'),    name='users_0'),    
    
]
