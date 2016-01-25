# Django imports
from django.contrib.auth.models import User

# Rest framework imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.mixins import *

# Project imports
from serializers import *

from admininterface.models import *

from rest_framework import generics
from rest_framework import mixins

# Configure logger
import logging
log = logging.getLogger(__name__)

class AdminViewset( ModelViewSet ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = AdminSerializer    
    permission_classes = [AllowAny]


    

class EventViewset( ModelViewSet ):
    model = Event
    queryset = Event.objects.filter()
    serializer_class = EventSerializer    
    permission_classes = [AllowAny]
        

class AdminListViewset( generics.ListCreateAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = AdminSerializer    
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        
        # Save serializer - Create superuser
        obj = serializer.save()
        obj.is_superuser = True
        obj.save()
        
        # Create associated data
        data = Data(user=obj)                
        data.save()
    

    
class AdminDetailViewset( generics.RetrieveUpdateDestroyAPIView ):

    #A simple ViewSet for viewing and editing accounts.
    model = User
    queryset = User.objects.filter(is_superuser=True)
    serializer_class = AdminSerializer    
    permission_classes = [AllowAny]


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