from __future__ import unicode_literals
import traceback

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Sum

from admininterface.models import *

# Configure logger
import logging
log = logging.getLogger(__name__)

"""
class EventAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event

class EventUserAppSerializer(serializers.ModelSerializer):
    event = EventAppSerializer()
    class Meta:
        model = EventUser
        fields = ('event', )

class UserAppSerializer(serializers.ModelSerializer):
    
    event = serializers.SerializerMethodField('event_field', required=False)        
    def event_field(self, obj):
        try:
            return EventAppSerializer(obj.eventuser.event).data
        except:
            return None
    
    class Meta:
        model = User
        fields = ('id', 'username', 'event')
"""        

class UserAppSerializer(serializers.ModelSerializer):
    
    event = serializers.SerializerMethodField('event_field', required=False)        
    def event_field(self, obj):
        try:
            return obj.eventuser.event.id
        except:
            return None
    
    class Meta:
        model = User
        fields = ('id', 'username', 'event','auth_token')

class EventCheckDetailAppSerializer(serializers.ModelSerializer):
    lastsubmit = serializers.SerializerMethodField('lastsubmit_field', required=False)        
    def lastsubmit_field(self, obj):
        return obj.trackdate.strftime("%d/%m/%y ") + \
                        obj.tracktime.strftime("%H:%M %p")

    checkintime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"], required=False)       
    checkouttime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"], required=False)
    class Meta:
        model = EventCheck
        fields = ('id', 'quantity', 'target', 'lastsubmit', 'completeflag', 
                  'checkintime', 'checkouttime')

class EventAppSerializer(serializers.ModelSerializer):

    pdfurl = serializers.SerializerMethodField('pdfurl_field', required=False)        
    def pdfurl_field(self, obj):
        try:
            return self.context['request'].scheme + '://' + self.context['request'].get_host() + obj.pdfdocument.url 
        except:
            traceback.print_exc()
            return obj.pdfdocument.url

    eventcheck = serializers.SerializerMethodField('eventcheck_field', required=False)        
    def eventcheck_field(self, obj):
        user = self.context['request'].user
        eventcheck = EventCheck.objects.filter(event=obj,user=user) \
                            .order_by('-checkintime').first()        
        return EventCheckDetailAppSerializer(eventcheck).data

    total = serializers.SerializerMethodField('total_field')        
    def total_field(self, obj):
        # Return total samplings for the given user and event
        try:
            user = self.context['request'].user
            total_dict=EventCheck.objects.filter(event=obj, user=user) \
                            .aggregate(total=Sum('quantity'))
            return total_dict['total']
        except:
            return 0
       
    class Meta:
        model = Event
        fields = ('id','title','description', 'videourl', 
                  'pdfurl', 'eventcheck', 'total')


class EventCheckAppSerializer(serializers.ModelSerializer):
    lastsubmit = serializers.SerializerMethodField('lastsubmit_field', required=False)        
    def lastsubmit_field(self, obj):
        try:
            return obj.trackdate.strftime("%d/%m/%y ") + \
                            obj.tracktime.strftime("%H:%M %p")
        except:
            return None
    checkintime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"], required=False)       
    checkouttime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"], required=False)
    
    class Meta:
        model = EventCheck
        fields = ('id', 'user', 'event', 'quantity', 'target', 'type', 'note', 'lastsubmit', 'completeflag',\
                  'checkintime', 'checkouttime','latitude', 'longitude', 'location')


   