import traceback
import json
from StringIO import StringIO
from datetime import datetime

# Django imports
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


from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
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
    permission_classes = [IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    
class AdminDetailViewset( generics.RetrieveUpdateDestroyAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = AdminSerializer        
    permission_classes = [IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

class EventUserListViewset( generics.ListCreateAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = EventUserSerializer      
    permission_classes = [IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
               

class EventUserDetailViewset( generics.RetrieveUpdateDestroyAPIView ):
    model = User
    queryset = User.objects.filter()
    serializer_class = EventUserSerializer   
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
        
class EventCheckGraphViewset( ViewSet ):

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def generate_graph_data(self, request, *args, **kwargs):
        event = Event.objects.get( id=kwargs['pk'] )
        eventcheck_list = EventCheck.objects.filter(event=event)
         
        # Generate graph data
        graph_data = eventcheck_list.values('trackdate') \
                     .annotate(quantity = Sum('quantity'), target = Sum('target') )         
        
        
        
        serializer = EventCheckSerializer(graph_data, many=True)
        json = JSONRenderer().render(serializer.data)

        
        # Quantity and target need to be read as int
        json_response = []            
        for item in serializer.data:
            json_response.append({ "trackdate": item['trackdate'],
                                   "quantity" : str(item['quantity']),
                                   "target" : str(item['target']),
                                  })
        return JsonResponse( json_response, safe=False )
