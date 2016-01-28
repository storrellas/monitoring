from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Event(models.Model):
    title         = models.CharField(max_length=30)
    description   = models.CharField(max_length=400)
    register_date = models.DateTimeField(default=timezone.now())
    pdfurl        = models.URLField(default='')
    videourl      = models.URLField(default='')
    pdf           = models.FileField(upload_to='event/',blank=True,null=True)
    
    def __unicode__(self):
       return self.title

class Data(models.Model):
    user     = models.OneToOneField(User, related_name='data')
    event    = models.ForeignKey(Event, null=True, blank=True)
    data     = models.CharField(max_length=400)
    
class EventUser(models.Model):
    user     = models.OneToOneField(User)
    event    = models.ForeignKey(Event)
    state    = models.IntegerField(default=0)
    
class EventCheck(models.Model):
    user         = models.ForeignKey(User)
    event        = models.ForeignKey(Event)
    checkouttime = models.DateTimeField(default=timezone.now())
    checkintime  = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
       return self.checkouttime

class TrackData(models.Model):
    user      = models.ForeignKey(User)
    event     = models.ForeignKey(Event)
    checkout  = models.ForeignKey(EventCheck)
    quantity  = models.IntegerField(default=0)    
    target    = models.IntegerField(default=0)
    type      = models.IntegerField(default=0)
    note      = models.CharField(default='',max_length=400)
    trackdate = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
       return self.event + self.checkout    