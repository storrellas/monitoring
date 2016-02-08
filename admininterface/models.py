from __future__ import unicode_literals

from django.db import models
from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):

    def _create_user(self, username, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        user = self.model(username=username,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, password, is_staff=False, is_superuser=False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, is_staff=True, is_superuser=True,
                                 **extra_fields)


class User(AbstractBaseUser,PermissionsMixin):

    # Common fields for everyone
    username    = models.CharField( max_length=30, blank=True, unique=True)
    first_name  = models.CharField( max_length=30, blank=True)
    last_name   = models.CharField( max_length=30, blank=True)
    is_staff    = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)    
    date_joined = models.DateTimeField(default=timezone.now)    
    phone       = models.CharField( max_length=30, blank=True)
    email       = models.CharField( max_length=30, blank=True)
    
    # Company
    cif    = models.CharField( max_length=30, blank=True)

    # EventUser
    gender     = models.CharField( max_length=30, blank=True)
    score      = models.CharField( max_length=30, blank=True)
    picture    = models.ImageField(upload_to='event/user/',blank=True,null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name


    def __unicode__(self):
        return self.username

class Event(models.Model):
    title         = models.CharField(max_length=30)
    description   = models.CharField(max_length=400)
    register_date = models.DateTimeField(default=timezone.now())
    videourl      = models.URLField(default='')
    pdfdocument   = models.FileField(upload_to='event/',blank=True,null=True)
    user          = models.ManyToManyField(User, related_name='event')
    
    def __unicode__(self):
       return self.title

    
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
    
    
    
    
    