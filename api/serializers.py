from __future__ import unicode_literals

from rest_framework import serializers
from django.contrib.auth.models import User

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
    

"""
class AdminSerializer(serializers.ModelSerializer):

    eventid = serializers.SerializerMethodField('eventid_field')        
    def eventid_field(self, user):
        try:
            return user.data.event.id
        except:
            return None
    
    class Meta:
        model = User
        fields = ('username', 'password','eventid')
"""

