#from apiv2.serializers import *
from admininterface.serializers import *
from admininterface.models import *

#from django.contrib.auth.models import User, Group
from django.db.models import Sum
from rest_framework.renderers import JSONRenderer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from datetime import datetime


user= User.objects.get(id=7)
event=Event.objects.get(id=2)
#eventcheck = EventCheck.objects.first()

