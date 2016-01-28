from django import forms
from django.contrib.auth.models import User
from django.conf import settings

from api.models import *

# Configure logger
import logging
log = logging.getLogger(__name__)

class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)

"""
known_tags = (
    (1, 'Choice 1'), (2, 'Choice 2'), (3, 'Choice 3'),
    (4, 'Choice 4'), (5, 'Choice 5'))

class EventForm(forms.Form):
    

    title         = forms.CharField(max_length=100)
    description   = forms.CharField(max_length=100)
    pdfdocument   = forms.FileField()
    videourl      = forms.URLField(max_length=100)
    
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)        
        log.info("Creating form in here")
        print args
        print kwargs
"""

class EventModelForm(forms.ModelForm):    

    class Meta:
        model = Event
        fields = ['title','description','pdfdocument','videourl']
            
        
        

        