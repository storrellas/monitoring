import logging

from django.views.generic import View
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound

from admininterface.models import Event
from feedback import forms
from feedback.exceptions import NoStartDateEndDateEvent, NoQuestionsDefined
from feedback.models import getAllQuestions, QuestionsDay, QuestionsUser, QuestionsEvent

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


class ListQuestions(View):
    template_name = "listquestions.html"

    def get(self, request, *args, **kwargs):
        context_data = dict()

        context_data['questions'] = getAllQuestions()
        context_data['form'] = forms.QuestionDayForm()
        return TemplateResponse(request, self.template_name, context_data)
    
    def post(self, request, *args, **kwargs):
        print request.POST, "<---(request.POST)"
        form = forms.QuestionDayForm(request.POST)
        if form.is_valid():
            """ Saving questions in form
            """
            form.save()
            r = "0"
        else:
            print form.errors
            logger.debug("Errors: {}".format(form.errors))
            r = "1"


        return redirect("{}?r={}".format(reverse('list_questions'), r))


class DeleteQuestion(View):
    def post(self, request):
        question_id = request.POST.get("question_id")
        typef = request.POST.get("type")
        if typef == "Day":
            O = QuestionsDay
        elif typef == "User":
            O = QuestionsUser
        elif typef == "Event":
            O = QuestionsEvent
        try:
            instance = O.objects.get(id=question_id)
        except:
            return HttpResponseNotFound('Element not found')
        instance.enabled = False
        instance.save()
        return redirect("{}?r=0".format(reverse('list_questions')))
