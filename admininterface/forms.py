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

class EventModelForm(forms.ModelForm):    

    class Meta:
        model = Event
        fields = ['title','description','pdfdocument','videourl']
    """            
    def save(self):
        
        print self.data['selno']
        # Updating
        if self.instance:
            for eventuser in self.instance.eventuser_set.all():
                print eventuser
                #eventuser.event = None
                #eventuser.save()
            event = self.instance
        else:        
        #Creating
            event = super(EventModelForm, self).save()        
        
        for id in self.data['selno'].split(','):
            log.info("Getting id " + str (id))
            user = User.objects.get(id=int(id))
            eventuser = EventUser.objects.get(user=user)
            eventuser.event = event
            eventuser.save()
            
            
        # Creating
        event = super(EventModelForm, self).save()
        for id in self.data['selno'].split(','):
            log.info("Getting id " + str (id))
            user = User.objects.get(id=int(id))
            eventuser = EventUser.objects.get(user=user)
            eventuser.event = event        
            eventuser.save()
        """

        

        