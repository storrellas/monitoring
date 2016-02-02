from __future__ import unicode_literals
import traceback

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Sum

from models import *

# Configure logger
import logging
log = logging.getLogger(__name__)



class DataSerializer(serializers.ModelSerializer):     
    class Meta:
        model = Data
        fields = ('event', )
 
class AdminSerializer(serializers.ModelSerializer):
    
    eventid = serializers.SerializerMethodField('eventid_field')        
    def eventid_field(self, user):
        try:                
            serializer = DataSerializer(user.data)
            return serializer.data['event']
        except:
            return None
    
    def create(self, validated_data):                
        obj = self.Meta.model.objects.create_superuser(username = self.data['username'],                                             
                                            password=self.data['password'],
                                            email='username@mail.com')
        try:            
            event = Event.objects.get(id=self.initial_data['eventid'][0])
        except:            
            event = None
                
        # Create associated data
        data = Data(user=obj, event= event) 
        data.save()        
        return obj        
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        
        try:
            event = Event.objects.get(id=self.initial_data['eventid'][0])
        except:
            event = None
        instance.data.event = event
        instance.save()
        instance.data.save()                 
        return instance                
    
    class Meta:
        model = User
        fields = ('username', 'password','eventid')

class EventUserSerializer(serializers.ModelSerializer):
        
    def create(self, validated_data):       
        obj = self.Meta.model.objects.create_user(username = validated_data['username'],                                             
                                                  password=validated_data['password'],
                                                  first_name=validated_data['first_name'])
        eventuser = EventUser(user=obj)
        eventuser.save()       
        return obj        
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()                 
        return instance                
    
    class Meta:
        model = User
        fields = ('username', 'password','first_name')

class EventUserEditSerializer(serializers.ModelSerializer):
            
    class Meta:
        model = User
        fields = ('username', 'first_name')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


class EventIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class TrackDataSerializer(serializers.Serializer):
    trackdate = serializers.DateField(format='%Y-%m-%d')
    quantity = serializers.IntegerField()
    target = serializers.IntegerField()
    
# API Serializers
##########################

class UserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserAppSerializer(user).data,
        'status' : 200
    }


class TrackDataAppSerializer(serializers.ModelSerializer):
    
    lastsubmit = serializers.SerializerMethodField('lastsubmit_field')        
    def lastsubmit_field(self, trackdata):
        return trackdata.trackdate.strftime("%d/%m/%y ") + trackdata.tracktime.strftime("%H:%M %p")

    total = serializers.SerializerMethodField('total_field')        
    def total_field(self, trackdata):
        total_dict=self.Meta.model.objects.filter(event=trackdata.event) \
                        .aggregate(total=Sum('quantity'))
        return total_dict['total']
    
    checkintime = serializers.SerializerMethodField('checkintime_field')        
    def checkintime_field(self, trackdata):
        try:
            return trackdata.eventcheck.checkintime.strftime("%d/%m/%y %H:%M %p")
        except:
            return None        

    checkouttime = serializers.SerializerMethodField('checkouttime_field')        
    def checkouttime_field(self, trackdata):
        try:
            return trackdata.eventcheck.checkouttime.strftime("%d/%m/%y %H:%M %p")
        except:
            return None
    
    class Meta:
        model = TrackData
        fields = ('eventcheck', 'checkouttime', 'checkintime', \
                  'completeflag','lastsubmit','total')

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
            lastsubmit = eventcheck.trackdate.strftime("%d/%m/%y ") + \
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


