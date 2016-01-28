from django import forms
from django.contrib.auth.models import User

from api.models import Event

class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)

"""
class EventForm(forms.Form):
    title = forms.CharField(label='title', max_length=100)
    description = forms.CharField(label='description', max_length=100)
    pdf      = forms.FieldField(label='pdf')
    videourl = forms.URLField(label='videourl', max_length=100)
    #eventuser_list = forms.ModelChoiceField(queryset=User.objects.all(), label='sergi', empty_label="(Nothing)")
"""    
