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


"""
class MapwaypointViewSet(viewsets.ViewSet):
    
    #A simple ViewSet for listing or retrieving mapwaypoints.
    
    def list(self, request):
        queryset = MapWaypoint.objects.all()
        serializer = MapWaypointSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = MapWaypoint.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = MapWaypointSerializer(user)
        return Response(serializer.data)
"""

##############################
## API 
##############################

class TaskViewset( ViewSet ):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        id = kwargs['pk']
        
        # Add event info
        user = User.objects.get(id=id)
        event = user.eventuser.event
        serializer = EventSerializer(user.eventuser.event)
        json_task = serializer.data
        json_task['pdfurl'] = request.scheme + '://' + request.get_host() + event.pdfdocument.url

        # Add TrackData info                
        track_data = TrackData.objects.filter(event=event,user=user) \
                        .order_by('-eventcheck__checkouttime').order_by('-trackdate').first()                                                                 
        serializer = TrackDataAppSerializer(track_data)
        json_task.update( serializer.data ) 
        
        """                        
        json_task.update(total_dict)
        json_task['lastsubmit'] = datetime.now()
        json_task['completeflag'] = 0
        json_task['checkoutid'] = 0
        """
        
        # Add status
        json_dict = {}
        json_dict['status'] = 200 
        json_dict['task'] = json_task
        
        return JsonResponse(json_dict)
    
    
    