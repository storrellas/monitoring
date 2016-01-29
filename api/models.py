from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Event(models.Model):
    title         = models.CharField(max_length=30)
    description   = models.CharField(max_length=400)
    register_date = models.DateTimeField(default=timezone.now())
    videourl      = models.URLField(default='')
    pdfdocument   = models.FileField(upload_to='event/',blank=True,null=True)
    
    def __unicode__(self):
       return self.title

class Data(models.Model):
    user     = models.OneToOneField(User, related_name='data')
    event    = models.ForeignKey(Event, null=True, blank=True)
    data     = models.CharField(max_length=400)
    
class EventUser(models.Model):
    user     = models.OneToOneField(User)
    event    = models.ForeignKey(Event, null=True, blank=True,on_delete=models.SET_NULL)
    state    = models.IntegerField(default=0)
    
class EventCheck(models.Model):
    user         = models.ForeignKey(User)
    event        = models.ForeignKey(Event)
    checkouttime = models.DateTimeField(default=timezone.now())
    checkintime  = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
       return self.user.username + "," + self.event.title + "," + self.checkouttime.strftime("%d/%m/%y")

class TrackData(models.Model):
    
    GOOD    = 1
    NEUTRAL = 2
    BAD     = 3
    FEEDBACK = (
        (GOOD, 1),
        (NEUTRAL, 2),
        (BAD, 3),
    )
    
    user       = models.ForeignKey(User)
    event      = models.ForeignKey(Event)
    eventcheck = models.OneToOneField(EventCheck)
    quantity   = models.IntegerField(default=0)    
    target     = models.IntegerField(choices=FEEDBACK, default=0)
    type       = models.IntegerField(default=1)
    note       = models.CharField(default='',max_length=400)
    trackdate  = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
       return self.user.username + "," + self.event.title + "," + self.trackdate.strftime("%d/%m/%y")    