from __future__ import unicode_literals

from rest_framework import serializers
from django.contrib.auth.models import User

from admininterface.models import *

class AdminSerializer(serializers.ModelSerializer):

    eventid = serializers.SerializerMethodField('eventid_field')        
    def eventid_field(self, user):        
        if not user.data.event:            
            return None
        else:
            return user.data.event.id
    
    
    class Meta:
        model = User
        fields = ('username', 'password','eventid')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


