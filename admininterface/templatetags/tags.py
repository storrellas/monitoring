# Django imports
from django import template
from django.conf import settings

from django.core.urlresolvers import reverse

from admininterface.models import *

register = template.Library()

@register.filter(name='sort')
def listsort(value):
  if isinstance(value,dict):
    new_dict = SortedDict()
    key_list = value.keys()
    key_list.sort()
    for key in key_list:
      new_dict[key] = value[key]
    return new_dict
  elif isinstance(value, list):
    new_list = list(value)
    new_list.sort()
    return new_list
  else:
    return value
listsort.is_safe = True

@register.filter(name='percentage')
def percentage(quantity, target):
    if target == 0:
        return 0
    return str(quantity*100/target) + '%'

@register.filter(name='company_extract')
def company_extract(event):
    company =""
    for user in event.user.all():
        if user.role == User.COMPANY:
            company += user.username
    
    # Remove the last comma 
    return company

@register.filter(name='eventuser_list')
def eventuser_list(event):
    userlist_str = ""
    
    for user in event.user.all():
        if user.role == User.EVENTUSER:
            userlist_str += user.username +", "
    
    # Remove the last comma
    userlist_str = userlist_str[:-2] 
    return userlist_str

@register.filter(name='location_list')
def location_list(event):
    locationlist_str = ""
    
    for location in event.location.all():
        locationlist_str += location.name +", "
    
    # Remove the last comma
    locationlist_str = locationlist_str[:-2] 
    return locationlist_str

@register.filter
def check_location(event,location):
    if event.location.filter(id=location.id).exists():
        return "checked"
    else:
        return ""
    
@register.filter
def product_list(event):
    productlist_str = ""
    for product in event.product.all():
        productlist_str += product.name +", "
    
    # Remove the last comma
    productlist_str = productlist_str[:-2] 
    return productlist_str

@register.filter
def check_product(event,product):
    if event.product.filter(id=product.id).exists():
        return "checked"
    else:
        return ""
