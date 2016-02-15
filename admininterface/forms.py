from django import forms

from models import *

# Configure logger
import logging
log = logging.getLogger(__name__)


class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)


class EventModelForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                                 input_formats=('%d/%m/%Y',), required=True)
    end_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                               input_formats=('%d/%m/%Y',), required=True)

    class Meta:
        model = Event
        fields = ['title', 'description', 'pdfdocument', 'videourl',
                  'start_date', 'end_date']

    # Called on validation of the form
    def clean(self):
        cleaned_data = super(EventModelForm, self).clean()
        if cleaned_data.get('end_date') < cleaned_data.get('start_date'):
            raise forms.ValidationError("Start date must be before End date")

class EventUserModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name',
                  'phone', 'email', 'gender', 'picture']
