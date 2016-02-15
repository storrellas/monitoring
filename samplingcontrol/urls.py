from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Examples:
    # url(r'^$', 'samplingcontrol.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('admininterface.urls')),
    url(r'^feedback/', include('feedback.urls')),
    #url(r'^api/v1/', include('apiv1.urls')),
    url(r'^api/v2/', include('apiv2.urls')),
        
] + \
static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

###########################
# Create groups
###########################
"""
from django.contrib.auth.models import Group 
Group.objects.get_or_create(name="Supervisor")
Group.objects.get_or_create(name="Company")
Group.objects.get_or_create(name="EventUser")
"""


