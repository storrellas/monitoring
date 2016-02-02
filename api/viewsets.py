import traceback
from StringIO import StringIO
from datetime import datetime

# Django imports
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.db.models import Sum

# Rest framework imports
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework.mixins import *
from rest_framework.parsers import JSONParser

from rest_framework import generics
from rest_framework import mixins
from rest_framework.renderers import JSONRenderer

# Project imports
from serializers import *
from models import *


from rest_framework.authentication import BasicAuthentication, SessionAuthentication 
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening



# Configure logger
import logging
log = logging.getLogger(__name__)


class AdminListViewset( generics.ListCreateAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = AdminSerializer      
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    
class AdminDetailViewset( generics.RetrieveUpdateDestroyAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = AdminSerializer        
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

class EventUserListViewset( generics.ListCreateAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = EventUserSerializer      
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
class EventUserDetailViewset( generics.RetrieveUpdateDestroyAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = EventUserSerializer        
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

class EventUserEditListViewset( generics.ListAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = EventUserEditSerializer      
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

class EventUserEditViewset( generics.UpdateAPIView ):
    model = User
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = EventUserEditSerializer    
    permission_classes = [AllowAny]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

class CheckAdminNameViewset( ViewSet ):
    
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    def checkname(self, request, *args, **kwargs):                        
        try:
            User.objects.get(username=request.POST.get['username'])
            return HttpResponseBadRequest()
        except: 
            return HttpResponse()
        
class EventViewset( ModelViewSet ):
    model = Event
    queryset = Event.objects.all()
    serializer_class = EventSerializer    
    permission_classes = [AllowAny]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)        
        

class EventMultiDeleteViewset( ViewSet ):

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def multidelete(self, request, *args, **kwargs):
        # Transform into native datatypes
        stream = StringIO(str(request.data['eventid']))
        data = JSONParser().parse(stream)
        # Apply serializer
        serializer = EventIdSerializer(data=data,many=True)
        if not serializer.is_valid():
            return HttpResponseBadRequest()
        
        # Delete corresponding items        
        for item in serializer.data:
            Event.objects.get(id=item['id']).delete()   
        return JsonResponse({})
        
        
class TrackDataGraphViewset( ViewSet ):

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def generate_graph_data(self, request, *args, **kwargs):
        event = Event.objects.get(id= kwargs['pk'] )
        trackdata_list = TrackData.objects.filter(event=event)
         
        # Generate graph data
        graph_data = trackdata_list.values('trackdate') \
                     .annotate(quantity = Sum('quantity'), target = Sum('target') )         
        
        
        
        serializer = TrackDataSerializer(graph_data, many=True)
        json = JSONRenderer().render(serializer.data)

        
        # Quantity and target need to be read as int
        json_response = []            
        for item in serializer.data:
            json_response.append({ "trackdate": item['trackdate'],
                                   "quantity" : str(item['quantity']),
                                   "target" : str(item['target']),
                                  })
        return JsonResponse( json_response, safe=False )


##############################
## API 
##############################

class GenerateUserTask(object):

    def generateUserTask(self,request,user,event, status = 200):
        serializer = EventSerializer(user.eventuser.event)
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
        json_dict['status'] = status 
        json_dict['task'] = json_task
        
        return JsonResponse(json_dict)

class TaskViewset( GenerateUserTask, ViewSet ):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        id = kwargs['pk']
        
        # Add event info
        user = User.objects.get(id=id)
        event = user.eventuser.event
        return self.generateUserTask(request,user,event)


class EventCheckinViewset( GenerateUserTask, ViewSet ):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


    def post(self, request, *args, **kwargs):
        
        try:
            # This is a constraint of the library used in the app
            data_processed = {}
            for key, value in request.data.iteritems():
                data_processed[key] = value
                if key == "userid":
                    data_processed['user'] = int(value)
                if key == "eventid":
                    data_processed['event'] = int(value)
                if key == "latitude" or key == "longitude":
                    data_processed[key] = float(value)
                                                    
            # Create EventCheckin
            #serializer = EventCheckinAppSerializer( data=request.data )
            serializer = EventCheckinAppSerializer( data=data_processed )

            
                
            # Check if already checkin
            event = Event.objects.get(id=data_processed['event'])
            user = User.objects.get(id=data_processed['user'])
            eventcheck_list = EventCheck.objects.filter(event=event,user=user) \
                        .order_by('-checkouttime').order_by('trackdata__trackdate')            
            if eventcheck_list.count() > 0:                
                eventcheck = eventcheck_list.first()
                if eventcheck.completeflag == 1:
                    return self.generateUserTask(request,user,event, status = 605)

            
            if not serializer.is_valid():                 
                raise Exception(serializer.errors)  
            eventcheck = serializer.save()
            
            # Return serializer.data
            #return JsonResponse(serializer.data)

            # Return UserTask - NOTE: This is very very weird
            return self.generateUserTask(request,eventcheck.user,eventcheck.event)             
            
        except:
            traceback.print_exc()
            return self.generateUserTask(request,eventcheck.user,eventcheck.event, status = 400)
            
class EventCheckoutViewset( GenerateUserTask, ViewSet ):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


    def post(self, request, *args, **kwargs):

        try:                                    
            eventcheck = EventCheck.objects.get(id=kwargs['eventcheck_id'] )                        
            
            # Check if exists trackdata            
            try:
                eventcheck.trackdata
            except:
                return self.generateUserTask(request,eventcheck.user,eventcheck.event, status = 607)  


            eventcheck.checkouttime = datetime.now()
            eventcheck.save()


            # Return UserTask - NOTE: This is very very weird
            return self.generateUserTask(request,eventcheck.user,eventcheck.event)             
            
        except:
            traceback.print_exc()
            return self.generateUserTask(request,eventcheck.user,eventcheck.event, status = 400)    


class TrackDataViewset( GenerateUserTask, ViewSet ):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


    def post(self, request, *args, **kwargs):
        try:
            #eventcheck = EventCheck.objects.get(id=kwargs['eventcheck_id'] )
            eventcheck = EventCheck.objects.first()
            
            # This is a constraint of the library used in the app
            data_processed = {}
            for key, value in request.data.iteritems():
                data_processed[key] = value
                if key == "userid":
                    data_processed['user'] = int(value)
                if key == "eventid":
                    data_processed['event'] = int(value)
            
                                             
            event = Event.objects.get(id=data_processed['event'])
            user = User.objects.get(id=data_processed['user'])
            
            # Check if already checkin
            event = Event.objects.get(id=data_processed['event'])
            user = User.objects.get(id=data_processed['user'])
            eventcheck_list = EventCheck.objects.filter(event=event,user=user) \
                        .order_by('-checkouttime').order_by('trackdata__trackdate')
            if eventcheck_list.count() > 0:                
                eventcheck = eventcheck_list.first()
                if eventcheck.completeflag == 1:
                    return self.generateUserTask(request,user,event, status = 608)
            else:
                return self.generateUserTask(request,user,event, status = 604)
                
            # Capture the trackdata    
            trackdata = TrackData(event=event, user=user, eventcheck=eventcheck)
            serializer = TrackDataAppSerializer( instance=trackdata,data=data_processed )
            if not serializer.is_valid():                 
                raise Exception(serializer.errors)  
            
            # Save serializer
            serializer.save()

            # Return UserTask - NOTE: This is very very weird
            return self.generateUserTask(request,eventcheck.user,eventcheck.event)             
            
        except:
            traceback.print_exc()
            return self.generateUserTask(request,eventcheck.user,eventcheck.event, status = 400)
    