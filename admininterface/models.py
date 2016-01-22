from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class Event(models.Model):
    title         = models.CharField(max_length=30)
    description   = models.CharField(max_length=400)
    register_date = models.DateTimeField(default=datetime.now())
    pdfurl        = models.URLField(default='')
    videourl      = models.URLField(default='')

class Data(models.Model):
    user     = models.ForeignKey(User)
    event    = models.ForeignKey(Event)
    data     = models.CharField(max_length=400)
    
    
class EventUser(models.Model):
    user     = models.OneToOneField(User)
    event    = models.ForeignKey(Event)
    state    = models.IntegerField(default=0)

    
class EventCheck(models.Model):
    user     = models.ForeignKey(User)
    event    = models.ForeignKey(Event)
    checkouttime = models.DateTimeField(default=datetime.now())
    checkintime = models.DateTimeField(default=datetime.now())


class TrackData(models.Model):
    user     = models.ForeignKey(User)
    event    = models.ForeignKey(Event)

    