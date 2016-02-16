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

class CompanyUserSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        
        print "In here company"
        print validated_data
                                
        obj = super(CompanyUserSerializer, self).create(validated_data)
               
        obj.set_password(validated_data['password'])
        obj.role = User.COMPANY       
        obj.save()
        
        try:
            event = Event.objects.get(id=self.initial_data['event'])
            event.user.clear()
            event.user.add(obj)
        except:
            log.info("Not able to find the event")
            pass
                
        return obj        
    
    def update(self, instance, validated_data):
        super(CompanyUserSerializer, self).update(instance, validated_data)
        
        try:
            instance.set_password(validated_data['password'])
            instance.save()
        except:
            print "No password provided"
            pass
        
        # Remove assigned user
        instance.event.clear()
        # Assign new user        
        try:
            event = Event.objects.get(id=self.initial_data['event'])  
            instance.event.add(event)
        except:
            log.info("Not able to find the event")
            pass
              
        return instance
                       
    password = serializers.CharField(required=False)
    class Meta:
        model = User 
        
class EventUserSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):                
        obj = self.Meta.model.objects.create_user(username = self.data['username'],                                             
                                            password=self.data['password'])
        obj.role = User.EVENTUSER 
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
        
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event

class EventCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields=('id', 'title')

class EventIdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class EventCheckSerializer(serializers.Serializer):
    trackdate = serializers.DateField(format='%Y-%m-%d')
    quantity = serializers.IntegerField()
    target = serializers.IntegerField()

class FileUploadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventCheckImage
        fields = ('photo', )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product

        