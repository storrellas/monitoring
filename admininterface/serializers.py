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

class EventUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventUser
        fields = ('description',)
        
class EventUserSerializer(serializers.ModelSerializer):
        
    def create(self, validated_data):
        obj = self.Meta.model.objects.create_user(username = validated_data['username'],                                             
                                    password=validated_data['password'])
        # Generate eventuser
        eventuser = EventUser(user=obj)
        eventuser.save()
        serializer = EventUserProfileSerializer(instance=eventuser,
                                                data=validated_data['eventuser'])
        if not serializer.is_valid():
            serializer.errors
            obj.delete()
            return None
        serializer.save()
        return obj
       
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()   
        return instance             

    eventuser = EventUserProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ('username', 'password', 'eventuser')

class EventUserEditSerializer(serializers.ModelSerializer):

    
    def update(self, instance, validated_data):
        #super(EventUserEditSerializer,self).update(instance, validated_data)
        instance.username = validated_data['username']
        instance.save()
        
        
        serializer = EventUserProfileSerializer(instance=instance.eventuser,
                                                data=validated_data['eventuser'])
        if not serializer.is_valid():
            serializer.errors
            obj.delete()
            return None
                       
        return instance
        
    eventuser = EventUserProfileSerializer(required=False)                
    class Meta:
        model = User
        fields = ('username', 'description', 'eventuser')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


class EventIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class EventCheckSerializer(serializers.Serializer):
    trackdate = serializers.DateField(format='%Y-%m-%d')
    quantity = serializers.IntegerField()
    target = serializers.IntegerField()
    
        