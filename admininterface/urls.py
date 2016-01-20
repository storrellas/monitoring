from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$',          TemplateView.as_view(template_name='sample.html'),        name='root'),
    url(r'^base/$',     TemplateView.as_view(template_name='base.html'),        name='root'),
]
