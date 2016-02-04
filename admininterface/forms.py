from django import forms
from django.contrib.auth.models import User
from django.conf import settings

from models import *

# Configure logger
import logging
log = logging.getLogger(__name__)

class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)

class EventModelForm(forms.ModelForm):    

    class Meta:
        model = Event
        fields = ['title','description','pdfdocument','videourl']


        

        