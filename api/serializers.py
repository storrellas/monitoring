from __future__ import unicode_literals
import traceback

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Sum

from models import *

# Configure logger
import logging
log = logging.getLogger(__name__)

class EventAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
   
class UserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class TrackDataAppSerializer(serializers.ModelSerializer):
    
    lastsubmit = serializers.SerializerMethodField('lastsubmit_field', required=False)        
    def lastsubmit_field(self, trackdata):
        try:
            return trackdata.trackdate.strftime("%d/%m/%y ") + trackdata.tracktime.strftime("%H:%M %p")
        except:
            return ""

    total = serializers.SerializerMethodField('total_field', required=False)        
    def total_field(self, trackdata):
        try:
            total_dict=self.Meta.model.objects.filter(event=trackdata.event) \
                            .aggregate(total=Sum('quantity'))
            return total_dict['total']
        except:
            return 0
    
    note = serializers.CharField(required=False,allow_blank=True)
    class Meta:
        model = TrackData
        fields = ('user','event','eventcheck', 'note', 
                  'lastsubmit','total', 'target', 'quantity')


class EventCheckAppSerializer(serializers.ModelSerializer):
    checkouttime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"])
    checkintime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"])
    
    
    total = serializers.SerializerMethodField('total_field')        
    def total_field(self, eventcheck):
        try:
            total_dict=TrackData.objects.filter(event=eventcheck.event) \
                            .aggregate(total=Sum('quantity'))
            return total_dict['total']
        except:
            return 0
        
    lastsubmit = serializers.SerializerMethodField('lastsubmit_field')        
    def lastsubmit_field(self, eventcheck):
        try:
            lastsubmit = eventcheck.trackdata.trackdate.strftime("%d/%m/%y ") + \
                            eventcheck.trackdata.tracktime.strftime("%H:%M %p")
            return lastsubmit
        except:
            return ""
    
    eventcheck = serializers.SerializerMethodField('eventcheck_field')        
    def eventcheck_field(self, eventcheck):
        return eventcheck.id
    
    class Meta:
        model = EventCheck
        fields = ('eventcheck', 'checkouttime', 'checkintime', \
                  'completeflag','lastsubmit','total')

class EventCheckinAppSerializer(serializers.ModelSerializer):

    checkintime = serializers.DateTimeField(format="%d/%m/%y %H:%M %p",input_formats=["%d/%m/%y %H:%M %p"], required=False)    
    class Meta:
        model = EventCheck
        fields = ('user','event','checkintime', 'latitude','longitude','location')

class TrackDataCheckinAppSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = TrackData
        fields = ('user','event','latitude','longitude','location')


