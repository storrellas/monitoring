from __future__ import unicode_literals

from rest_framework import serializers
from django.contrib.auth.models import User

from admininterface.models import *

# Configure logger
import logging
log = logging.getLogger(__name__)

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event

        

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
    
    class Meta:
        model = User
        fields = ('username', 'password','eventid')


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

