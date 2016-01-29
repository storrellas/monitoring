# Django libs
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

# Thrid-party libs
from import_export import resources

# Project libs
from models import *

#@admin.register(Event)
#class EventAdmin(admin.ModelAdmin):
#    pass

app_models = apps.get_app_config('api').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass

#admin.site.unregister(User)
#admin.site.unregister(Group)




class TrackDataResource(resources.ModelResource):

    class Meta:
        model = TrackData
        fields = ('user__username', 'event__title', 'quatity', 'target', 'type', 'trackdate')
        
        