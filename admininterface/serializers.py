from __future__ import unicode_literals
import traceback

from rest_framework import serializers
from django.db.models import Sum

from models import *

# Configure logger
import logging
log = logging.getLogger(__name__)


class AdminSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):                
        obj = self.Meta.model.objects.create_superuser(username = self.data['username'],                                             
                                            password=self.data['password'])
        obj.save()
        return obj        
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()               
        return instance                
    
    class Meta:
        model = User
        fields = ('username', 'password')
        
class EventUserSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):                
        obj = self.Meta.model.objects.create_user(username = self.data['username'],                                             
                                            password=self.data['password'])
        obj.save()
        return obj        
    
    def update(self, instance, validated_data):
        super(EventUserSerializer, self).update(instance, validated_data)
        
        try:
            instance.set_password(validated_data['password'])
            instance.save()
        except:
            print "No password provided"
            pass        
        return instance
                       
    password = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ('username', 'password')        
        
"""
class EventUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
"""

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


class EventIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class EventCheckSerializer(serializers.Serializer):
    trackdate = serializers.DateField(format='%Y-%m-%d')
    quantity = serializers.IntegerField()
    target = serializers.IntegerField()

        