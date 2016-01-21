from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Examples:
    # url(r'^$', 'samplingcontrol.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^login/', 'rest_framework_jwt.views.obtain_jwt_token', name='api-login'),       
    url(r'^docs/', include('rest_framework_swagger.urls'),       name='api-docs'),
]

