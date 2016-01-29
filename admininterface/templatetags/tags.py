# Django imports
from django import template
from django.conf import settings

from django.core.urlresolvers import reverse



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
    return str(quantity*100/target) + '%'