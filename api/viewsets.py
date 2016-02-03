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

# Project imports
from serializers import *
from models import *


# Configure logger
import logging
log = logging.getLogger(__name__)



class ErrorCodeSet(object):
    ERR_USER_NO_ERROR          = 200
    
    ERR_USER_NOT_FOUND         = 600
    ERR_USER_INVALID_PASSWORD  = 601
    ERR_USER_NO_REPORTED       = 602
    ERR_USER_NO_EVENT_MEMBER   = 603
    ERR_USER_NO_CHECKIN        = 604
    ERR_USER_ALREADY_CHECKIN   = 605
    ERR_USER_NOT_EXIST_CHECKIN = 606
    ERR_USER_CHECKOUT_FAILED   = 607
    ERR_USER_ALREADY_CHECKOUT  = 608
    

class JsonAppInterface(object):

    def paramterTranslateInput(self, data):
        # This is a constraint of the library used in the app
        data_processed = {}
        for key, value in data.iteritems():
            if key == "userid":
                data_processed['user'] = int(value)
            elif key == "eventid":
                data_processed['event'] = int(value)
            elif key == "checkoutid":
                data_processed['eventcheck'] = int(value)
            else:
                data_processed[key] = value
        return data_processed

    def paramterTranslateOuput(self, data):
        # This is a constraint of the library used in the app
        data_processed = {}
        for key, value in data.iteritems():
            if key == "eventcheck":
                data_processed['checkoutid'] = int(value)
            else:
                data_processed[key] = value
        return data_processed

    def jsonAppResponse(self, dict, status = ErrorCodeSet.ERR_USER_NO_ERROR):
        dict['status'] = status
        return JsonResponse(dict)

    def jsonAppTaskResponse(self,request, user, event, status = ErrorCodeSet.ERR_USER_NO_ERROR):
        serializer = EventAppSerializer(user.eventuser.event)
        json_task = serializer.data
        json_task['pdfurl'] = request.scheme + '://' + request.get_host() + event.pdfdocument.url

        # Complete JSON with EventCheck
        eventcheck = EventCheck.objects.filter(event=event,user=user) \
                        .order_by('-checkouttime').order_by('trackdata__trackdate').first()
        if eventcheck is not None:
            serializer = EventCheckAppSerializer(eventcheck)
            json_task.update( serializer.data )
        
        # Add status
        json_dict = {}
        json_dict['task'] = self.paramterTranslateOuput(json_task)        
        return self.jsonAppResponse(json_dict, status)

class LoginAppViewset( JsonAppInterface, ViewSet ):
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

        try:
            User.objects.get(username=username)
        except:
            return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_NOT_FOUND)
        

        # Check if user exists
        user = authenticate (username=username, password=password)
        if user is None:
            return self.jsonAppResponse({}, status=ErrorCodeSet.ERR_USER_INVALID_PASSWORD)
        serializer = UserAppSerializer(user)
                
        # Add status
        json_dict = {}
        json_dict['id']       = serializer.data['id']
        json_dict['username'] = serializer.data['username']        
        return self.jsonAppResponse(json_dict)
             


class TaskViewset( JsonAppInterface, ViewSet ):
    """
    Retrieves the current task 
    """

    def post(self, request, *args, **kwargs):
        """
        ---
        parameters:
        - name: userid
          description: userid
          required: true
          type: int
          paramType: form
        - name: eventid
          description: eventid
          required: true
          type: int
          paramType: form
        """
        # Add event info
        user = User.objects.get(id=request.data['userid'])
        event = user.eventuser.event
        return self.jsonAppTaskResponse(request, user, event)


class EventCheckinViewset( JsonAppInterface, ViewSet ):
    """
    Enables the user to perform checkin operation 
    """

    def post(self, request, *args, **kwargs):
        """
        ---
        parameters:
        - name: userid
          description: user id from which retrieve tasks
          required: true
          type: int
          paramType: form
        - name: eventid
          required: true
          type: int
          paramType: form
        - name: latitude
          required: true
          type: float
          paramType: form          
        - name: longitude
          required: true
          type: float
          paramType: form
        - name: location
          required: false
          type: string
          paramType: form
        """
        
        
        try:
            # Adapt parameter coming from app
            data_processed = self.paramterTranslateInput(request.data)
            
            # Get user and event
            event = Event.objects.get(id=data_processed['event'])
            user = User.objects.get(id=data_processed['user'])

            
                
            # Check if already checkin
            eventcheck = EventCheck.objects.filter(event=event,user=user) \
                            .order_by('-checkouttime').first()            
            if eventcheck is not None:                
                if eventcheck.completeflag == 0:
                    return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_ALREADY_CHECKIN)

            # Create serializer
            serializer = EventCheckinAppSerializer( data=data_processed )            
            if not serializer.is_valid():                 
                raise Exception(serializer.errors)  
            eventcheck = serializer.save()


            # Return UserTask - NOTE: This is very very weird
            return self.jsonAppTaskResponse(request,eventcheck.user,eventcheck.event)             
            
        except:
            traceback.print_exc()
            return self.jsonAppResponse({}, status = 400)
            
class EventCheckoutViewset( JsonAppInterface, ViewSet ):
    """
    Enables the user to perform checkout operation 
    """

    def post(self, request, *args, **kwargs):
        """
        ---
        parameters:
        - name: userid
          description: user id from which retrieve tasks
          required: true
          type: int
          paramType: form
        - name: eventid
          required: true
          type: int
          paramType: form
        - name: checkoutid
          required: true
          type: int
          paramType: form        
        """


        try:
                                  
            # Adapt parameter coming from app
            data_processed = self.paramterTranslateInput(request.data)

            # Get user and event
            event = Event.objects.get(id=data_processed['event'])
            user = User.objects.get(id=data_processed['user'])
            
            # Check if not checkin
            eventcheck = EventCheck.objects.filter(event=event,user=user) \
                            .order_by('-checkouttime').first()            
            if eventcheck is None:                
                if eventcheck.completeflag == 1:
                    return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_ALREADY_CHECKOUT)
            
            
            # Check if exists trackdata            
            try:
                eventcheck.trackdata
            except:
                return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_NO_REPORTED)  

            # Save checkout
            eventcheck.checkouttime = datetime.now()
            eventcheck.completeflag = 1
            eventcheck.save()

            # Return Task response
            return self.jsonAppTaskResponse(request,eventcheck.user,eventcheck.event)                         
        except:
            traceback.print_exc()
            return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_NOT_EXIST_CHECKIN)
            #return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_CHECKOUT_FAILED)        


class TrackDataViewset( JsonAppInterface, ViewSet ):
    """
    Enables the user to report
    """

    def post(self, request, *args, **kwargs):
        """
        ---
        parameters:
        - name: userid
          description: user id from which retrieve tasks
          required: true
          type: int
          paramType: form
        - name: eventid
          required: true
          type: int
          paramType: form
        - name: checkoutid
          required: true
          type: int
          paramType: form

        - name: note
          required: true
          type: string
          paramType: form
        - name: quantity
          required: true
          type: int
          paramType: form
        - name: total
          required: true
          type: int
          paramType: form
        - name: type
          description: (good=1; neutral=2; bad=3)
          required: true
          type: int
          paramType: form            
        """
        
        try:
            # Adapt parameter coming from app
            data_processed = self.paramterTranslateInput(request.data)
                                             
            # Get user and event                                             
            event = Event.objects.get(id=data_processed['event'])
            user = User.objects.get(id=data_processed['user'])
            
                        
            # Check if not check in
            eventcheck = EventCheck.objects.filter(event=event,user=user) \
                            .order_by('-checkouttime').first()            
            if eventcheck is not None:                
                if eventcheck.completeflag == 1:          
                    return self.jsonAppResponse({}, status = ErrorCodeSet.ERR_USER_NO_CHECKIN)
                        
            serializer = TrackDataAppSerializer( data=data_processed )
            if not serializer.is_valid():
                raise Exception(serializer.errors)  
            
            # Save serializer
            serializer.save()
            
            # Return Task response
            return self.jsonAppTaskResponse(request, user, event)             
            
        except:
            traceback.print_exc()
            return self.jsonAppResponse({}, status = 400)
    