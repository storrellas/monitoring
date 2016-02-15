import logging

from django.views.generic import View
from django.template.response import TemplateResponse

from admininterface.models import Event
from feedback import forms
from feedback.exceptions import NoStartDateEndDateEvent, NoQuestionsDefined

logger = logging.getLogger("django")

class FeedBack(View):
    template_name = "formview.html"

    def get(self, request, id, *args, **kwargs):
        context_data = dict()
        event = Event.objects.get(id=id)
        context_data['event'] = event
        if not request.user.has_assigned(event):
            return TemplateResponse(request, self.template_name, { 'no_view': True})
        try:
            context_data['form'] = forms.FeedbackForm(event, request.user)
        except NoStartDateEndDateEvent:
            return TemplateResponse(request, self.template_name, { 'no_dates': True})
        except NoQuestionsDefined:
            return TemplateResponse(request, self.template_name, { 'no_questions': True})

        return TemplateResponse(request, self.template_name, context_data)

    def post(self, request, id, *args, **kwargs):
        logger.debug("Saving feedback form")
        event = Event.objects.get(id=id)
        context_data = dict()
        context_data['event_name'] = event.title

        form = forms.FeedbackForm(event, request.user, request.POST)
        if form.is_valid():
            logger.debug("Form is valid")
            form.save()
        else:
            logger.debug("Form is not valid")

        context_data['form'] = form
        context_data['confirm_save'] = True
        context_data['event_id'] = id
        
        return TemplateResponse(request, self.template_name, context_data)
