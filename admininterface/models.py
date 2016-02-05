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
    MALE = 'MALE'
    MALE = 'FEMALE'
    OTHER = 'OTHER'
    GENDER = (
              ('male', 'MALE'),
              ('female', 'FEMALE'),
              ('other', 'OTHER')
              )
    
    user     = models.OneToOneField(User)
    event    = models.ForeignKey(Event, null=True, blank=True,on_delete=models.SET_NULL)
    phone    = models.CharField(max_length=400, default='')
    description = models.CharField(max_length=400, default='')
    gender    = models.CharField(max_length=10, choices=GENDER, default=OTHER)
    score     = models.IntegerField(default=0)
    picture   = models.FileField(upload_to='eventuser/')
    
class Company(models.Model):
    user     = models.OneToOneField(User)
    address  = models.ForeignKey(Event, null=True, blank=True,on_delete=models.SET_NULL)
    cif      = models.CharField(max_length=400, default='')
    contanct = models.CharField(max_length=400, default='')
    phone    = models.CharField(max_length=400, default='')
    
class SuperVisor(models.Model):
    user     = models.OneToOneField(User)
    address  = models.ForeignKey(Event, null=True, blank=True,on_delete=models.SET_NULL)
    cif      = models.CharField(max_length=400, default='')
    contanct = models.CharField(max_length=400, default='')
    phone    = models.CharField(max_length=400, default='')
    
class EventCheck(models.Model):
    
    UNDEFINED = 0
    GOOD      = 1
    NEUTRAL   = 2
    BAD       = 3
    FEEDBACK = (
        (UNDEFINED, 0),
        (GOOD, 1),
        (NEUTRAL, 2),
        (BAD, 3),
    )
    
    user         = models.ForeignKey(User)
    event        = models.ForeignKey(Event)
    
    quantity     = models.IntegerField(default=0)    
    target       = models.IntegerField(default=0)
    type         = models.IntegerField(choices=FEEDBACK, default=UNDEFINED)
    note         = models.CharField(default='',max_length=400)
    brief_opened = models.BooleanField(default=False)
    trackdate    = models.DateField(auto_now=True)
    tracktime    = models.TimeField(auto_now=True)

    checkintime  = models.DateTimeField(default=timezone.now())
    checkouttime = models.DateTimeField(null=True, blank=True)
    completeflag = models.BooleanField(default=False)

    latitude     = models.FloatField(default=0.0)
    longitude    = models.FloatField(default=0.0)
    location     = models.CharField(default='', max_length=400)    

    def __unicode__(self):
        if self.trackdate is not None and self.tracktime is not None:
            return self.user.username + "," + self.event.title + "," + self.trackdate.strftime("%d/%m/%y") + "," + self.tracktime.strftime("%d/%m/%y")
        else: 
            return self.user.username + "," + self.event.title

class EventCheckImage(models.Model):
    photo         = models.ImageField(upload_to='event/photo/',blank=True,null=True)
    eventcheck    = models.ForeignKey(EventCheck)

class Product(models.Model):
    event    = models.ForeignKey(Event,null=True, blank=True, related_name='products')
    name     = models.CharField(default='', max_length=400) 
    brand    = models.CharField(default='', max_length=400)
    format   = models.CharField(default='', max_length=400)
    
    
    
    
    