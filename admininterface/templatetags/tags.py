# Django imports
from django import template
from django.conf import settings

from django.core.urlresolvers import reverse

from admininterface.models import *

register = template.Library()

 

@register.inclusion_tag('sidebar.html', takes_context=True)
def sidebar(context):
    request = context['request']
    url = request.path    
    if reverse('base') == request.path:
        pass
    return {'url': "sergi" }


@register.filter(name='percentage')
def percentage(quantity, target):
    if target == 0:
        return 0
    return str(quantity*100/target) + '%'

@register.filter(name='eventuser_list')
def eventuser_list(event):
    userlist_str = ""
    
    for user in event.user.all():
        if user.role == User.EVENTUSER:
            userlist_str += user.username +", "
    
    # Remove the last comma
    userlist_str = userlist_str[:-2] 
    return userlist_str
