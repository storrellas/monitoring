import traceback
from StringIO import StringIO
from datetime import datetime

# Django imports
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.db.models import Sum
from django.contrib.auth import authenticate
from django.utils import timezone

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
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated

# Project imports
from serializers import *
from admininterface.models import *

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


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
       

        serializer = UserInputAppSerializer(data=request.data)
        if not serializer.is_valid():
            raise APIException( serializer.errors )
                
        # Authenticate user
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']        
        user = authenticate (username=username, password=password)
        if user is None:
            raise APIException("Credentials were not valid" )
        
        if user.role != User.EVENTUSER:
            raise APIException( "User is not EventUser" )
            
        # Return userdata            
        serializer = UserAppSerializer(user)            
        return JsonResponse(serializer.data)

class EventListAppViewset( generics.ListAPIView ):
    model = Event
    serializer_class = EventAppSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]

class EventDetailAppViewset( generics.RetrieveAPIView ):
    model = Event
    serializer_class = EventAppSerializer
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]

class EventCheckAppViewset(generics.ListAPIView):
    model = EventCheck
    queryset = EventCheck.objects.all()
    serializer_class = EventCheckAppSerializer
    permission_classes = [IsAuthenticated]

class EventCheckInAppViewset(generics.CreateAPIView):
    model = EventCheck
    queryset = EventCheck.objects.all()
    serializer_class = EventCheckAppSerializer
    permission_classes = [IsAuthenticated]

    def create(self,request, *args, **kwargs):
        
        # Check if already checkin
        event=Event.objects.get(id=request.data['event'])
        user=User.objects.get(id=request.data['user'])
        eventcheck = EventCheck.objects.filter(event=event,user=user) \
                    .order_by('-checkintime').first()
        if eventcheck is not None:
            if eventcheck.completeflag == False:
                raise APIException("You already made checkin")

        # Continue with flow
        return super(EventCheckInAppViewset,self).create(request, *args, **kwargs)
        
        
    
    
class EventCheckOutAppViewset(generics.UpdateAPIView):
    model = EventCheck
    queryset = EventCheck.objects.all()
    serializer_class = EventCheckAppSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self,request, *args, **kwargs):

        # Check if not checkin
        event=Event.objects.get(id=request.data['event'])
        user=User.objects.get(id=request.data['user'])
        eventcheck = EventCheck.objects.filter(event=event,user=user) \
                    .order_by('-checkintime').first()
        if eventcheck is not None:                    
            if eventcheck.completeflag == True:
                raise APIException("You did not check in or you already checkout")
            if eventcheck.type == EventCheck.UNDEFINED:
                raise APIException("You did not report")
            """
            if eventcheck.eventcheckimage_set.count() < 3:
                raise APIException("You are missing some pictures to checkout")
            """
              
        # Mark as completed
        instance=self.get_object()
        instance.completeflag = True
        instance.checkouttime = datetime.now()
        instance.save()
        
        return super(EventCheckOutAppViewset,self).update(request, *args, **kwargs)

    

class EventCheckReportAppViewset(generics.UpdateAPIView):
    model = EventCheck
    queryset = EventCheck.objects.all()    
    serializer_class = EventCheckAppSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self,request, *args, **kwargs):        
                
        # Check if not checkin
        event=Event.objects.get(id=request.data['event'])
        user=User.objects.get(id=request.data['user'])
        eventcheck = EventCheck.objects.filter(event=event,user=user) \
                    .order_by('-checkintime').first()
        if eventcheck is not None:
            if eventcheck.completeflag == True:
                raise APIException("You did not check in")
        
        obj = self.get_object()
        quantity = obj.quantity
        target = obj.target
        note = obj.note
        
        # Apply serializer
        serializer = EventCheckAppSerializer(instance=obj, data=request.data) 
        if serializer.is_valid():
            obj = serializer.save()
            obj.quantity += quantity
            obj.target += target
            obj.note   = note + ";" + obj.note
            obj.save()
        else:
            raise APIException(serializer.errors)
        
        serializer = EventCheckAppSerializer(obj,context={'request':request})
        return JsonResponse(serializer.data)
        
        # NOTE: This is avoided to get multiple report available
        #return super(EventCheckReportAppViewset,self).update(request, *args, **kwargs)
    
 
class EventCheckPhotoAppViewset(ViewSet):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args,**kwargs):
        # Capture eventcheck
        eventcheck = EventCheck.objects.get(id=kwargs['pk'])
        
        # Capture form
        serializer = UploadFileSerializer(request.POST, request.FILES)
        if serializer.is_valid():

            obj = EventCheckImage(photo=request.FILES['file'], eventcheck=eventcheck)
            obj.save()

        return Response(status=204)
