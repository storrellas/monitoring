import traceback
from StringIO import StringIO
from datetime import datetime

# Django imports
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.db.models import Sum
from django.contrib.auth import authenticate

# Rest framework imports
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.mixins import *
from rest_framework.parsers import JSONParser

from rest_framework import generics
from rest_framework import mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import ValidationError

# Project imports
from serializers import *
from admininterface.models import *


class LoginAppViewset( ViewSet ):
    """
    Login operation
    """

    def post(self, request, *args, **kwargs):
        """
        ---
        parameters:
        - name: username
          description: username
          required: true
          type: string
          paramType: form
        - name: password
          paramType: form
          required: true
          type: string
        """
        # Get paramters
        username = request.data['username']
        password = request.data['password']
        
        user = authenticate (username=username, password=password)
        if user is None:
            if user.groups.filter(name='EventUser').exists() == False:
                dict = {}
                dict['error'] = "Credentials not valid"
                raise ValidationError( dict )
            
        # Return userdata            
        serializer = UserAppSerializer(user)            
        return JsonResponse(serializer.data)

class EventAppViewset( generics.RetrieveAPIView ):
    model = Event
    serializer_class = EventAppSerializer
    queryset = Event.objects.all()



class EventCheckInAppViewset(generics.CreateAPIView):
    model = EventCheck
    queryset = EventCheck.objects.all()
    serializer_class = EventCheckInAppSerializer
            
    def create(self,request, *args, **kwargs):
        serializer = EventCheckInAppSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return APIException('Didnt work')
    
    
class EventCheckOutAppViewset(generics.UpdateAPIView):
    model = EventCheck
    queryset = EventCheck.objects.all()
    serializer_class = EventCheckInAppSerializer
    
    def update(request, *args, **kwargs):
        serializer = EventCheckInAppSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return APIException('Didnt work')
    

  