from __future__ import unicode_literals
import traceback

from rest_framework import serializers
from django.db.models import Sum
from datetime import datetime

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
        obj = super(CompanyUserSerializer, self).create(validated_data)
               
        obj.set_password(validated_data['password'])
        obj.is_staff = True
        obj.is_active = True
        obj.date_joined=datetime.now()
        obj.role = User.COMPANY       
        obj.save()
                        
        return obj        
    
    def update(self, instance, validated_data):
        super(CompanyUserSerializer, self).update(instance, validated_data)
        
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

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        