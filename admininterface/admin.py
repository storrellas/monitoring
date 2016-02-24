# Django libs
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

# Thrid-party libs
from import_export import resources,fields

# Project libs
from models import *


app_models = apps.get_app_config('admininterface').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass

#admin.site.unregister(User)
#admin.site.unregister(Group)

class EventCheckDateField(fields.Field):
    def export(self,object):
        return object.trackdate.strftime("%d/%m/%Y") + " " + object.tracktime.strftime("%H:%M:%S")

class PercentField(fields.Field):
    def export(self,object):
        if object.quantity == 0:
            return 0
        return (object.target*100)/object.quantity

class LocationField(fields.Field):
    def export(self,object):
        return object.location.name + " " + object.location.address + "," + object.location.city

class EventCheckResource(resources.ModelResource):
    eventcheckdate  = EventCheckDateField(column_name='Date')
    percent         = PercentField(column_name='Percent(%)')
    username        = fields.Field(attribute='user__username',column_name='Username')
    quantity        = fields.Field(attribute='quantity',column_name='Quantity')
    target          = fields.Field(attribute='target',column_name='Target')
    type            = fields.Field(attribute='type',column_name='Feedback')
    note            = fields.Field(attribute='note',column_name='Comment')
    event           = fields.Field(attribute='event__title',column_name='Event')
    address         = LocationField(column_name='Address')
    
    def dehydrate_checkintime(self, object):
        return object.checkintime.strftime("%d/%m/%Y %H:%M:%S")

    def dehydrate_checkouttime(self, object):
        return object.checkintime.strftime("%d/%m/%Y %H:%M:%S")
    
    class Meta:
        model = EventCheck
        fields = ('username', 'eventcheckdate', 'checkintime','checkouttime',\
                  'quantity', 'target','percent','type','event','address')
        export_order = ('eventcheckdate', 'username', 'checkintime','checkouttime',\
                  'quantity', 'target','percent','type', 'note', 'event','address')