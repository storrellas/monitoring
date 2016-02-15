from django import template

register = template.Library()

@register.inclusion_tag('formtemplate.html')
def showFeedbackForm(form, event):
    """
    """
    return { 
        'form': form, 'event': event
    }