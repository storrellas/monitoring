# Django imports
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

# Rest framework imports
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework.mixins import *

from rest_framework import generics
from rest_framework import mixins


# Project imports
from serializers import *
from admininterface.models import *

from rest_framework.authentication import BasicAuthentication

from rest_framework.authentication import SessionAuthentication 
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

class EventViewset( ModelViewSet ):
    model = Event
    queryset = Event.objects.filter()
    serializer_class = EventSerializer    
    permission_classes = [AllowAny]

class CheckAdminNameViewset( ViewSet ):
    
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    def checkname(self, request, *args, **kwargs):                        
        try:
            User.objects.get(username=request.POST.get['username'])
            return HttpResponseBadRequest()
        except: 
            return HttpResponse()
        
        
        
        

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