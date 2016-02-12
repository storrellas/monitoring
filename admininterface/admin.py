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


app_models = apps.get_app_config('admininterface').get_models()
for model in app_models:
    try:
        pass#admin.site.register(model)
    except AlreadyRegistered:
        pass

#admin.site.unregister(User)
#admin.site.unregister(Group)




class EventCheckResource(resources.ModelResource):

    class Meta:
        model = EventCheck
        fields = ('user__username', 'event__title', 'quatity', 'target', 'type', 'trackdate')