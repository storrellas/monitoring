
import logging

from django import forms
from datetime import datetime

from admininterface.models import User
from feedback.exceptions import NoStartDateEndDateEvent, NoQuestionsDefined
from feedback import models

logger = logging.getLogger("")

 
class FeedbackForm(forms.Form):

    def _create_fields_dates(self, event):
        """ Creates the questions for each day.
        """
        # Num days between end_Date and start_date
        questions = models.QuestionsDay.objects.filter(enabled=True)

        #num_days = (event.end_date.date() - event.start_date.date()).days+1
        print event.end_date, event.start_date
        for day in event.getDays():
            print day
            #day = (event.start_date + timedelta(days=da)).date()

            # For each day, we specify a field for all questions
            for question in questions:
                # Retrieving initial
                initial = models.QuestionsDay.objects.getInitial(event,
                                                                 question,
                                                                 day=day)

                #questiontext = question.full_sentence#"{} ({})".format(question.text, day)
                t = (day.strftime("%Y%m%d"), question.id)
                fieldname = 'questionday_%s_%s' % t
                miniform = AnswersDayForm(question.text)
                self.fields[fieldname] = miniform.fields['text']
                self.fields[fieldname].initial = initial
                self.fields[fieldname].label = day.strftime("%d-%m-%Y")
                self.fields[fieldname].label = question.full_sentence(day)

    def _create_fields_users(self, event):
        """ Creates the questions for each user.
        """
        # Num days between end_Date and start_date
        questions = models.QuestionsUser.objects.filter(enabled=True)
        for user in event.user.all():
            # For each pair user, questions
            for question in questions:
                # Retrieving initial
                initial = models.QuestionsUser.objects.getInitial(event,
                                                                  question,
                                                                  user=user)

                fieldname = 'questionuser_%s_%s' % (user.id, question.id)
                miniform = AnswersUserForm(question.text)
                self.fields[fieldname] = miniform.fields['text']
                self.fields[fieldname].initial = initial
                self.fields[fieldname].label = question.full_sentence(user)

    def _create_fields_event(self, event):
        """ Creates the questions for each user.
        """
        # Num days between end_Date and start_date
        questions = models.QuestionsEvent.objects.filter(enabled=True)

        for question in questions:
            # Retrieving initial
            initial = models.QuestionsEvent.objects.getInitial(event, question)

            fieldname = 'questionevent_%s' % (question.id)
            miniform = AnswersEventForm(question.text)
            self.fields[fieldname] = miniform.fields['text']
            self.fields[fieldname].initial = initial
            self.fields[fieldname].label = question.full_sentence()

    def _save_answer_user(self, user_id, question_id, answer_text):
        """ Saves the answer from a feedback form to the corresponsing model
        """
        q = models.QuestionsUser.objects.get(id=question_id)
        u = User.objects.get(id=user_id)
        e = self.event
        o = models.AnswersUser.objects.filter(user=u, question=q, event=e)
        if len(o):
            o = o[0]
            o.text = answer_text
        else:
            # New answer, we create the object
            o = models.AnswersUser(user=u, question=q, event=e,
                                   text=answer_text)
        o.save()

    def _save_answer_day(self, day, question_id, answer_text):
        q = models.QuestionsDay.objects.get(id=question_id)
        e = self.event
        d = models.FeedbackDay.objects.filter(event=e, day=day)
        if len(d):
            d = d[0]
        else:
            # Creating FeedbackDay if it does not exist for this event
            d = models.FeedbackDay(event=e, day=day)
            d.save()
        # Using the feedbackday to save the answer.
        o = models.AnswersDay.objects.filter(feedbackday=d, question=q)
        if len(o):
            o = o[0]
            o.text = answer_text
        else:
            # New answer, we create the object
            o = models.AnswersDay(feedbackday=d, question=q, text=answer_text)
        o.save()

    def _save_answer_event(self, question_id, answer_text):
        q = models.QuestionsEvent.objects.get(id=question_id)
        e = self.event
        o = models.AnswersEvent.objects.filter(question=q, event=e)
        if len(o):
            o = o[0]
            o.text = answer_text
        else:
            # New answer, we create the object
            o = models.AnswersEvent(question=q, event=e, text=answer_text)
        o.save()

    def __init__(self, event, *args, **kwargs):
        """ We generate the form according to the event. We need a field
        to specify the feedback for each day of the duration of the campaign.

        Raises:
          NoStartDateEndDateEvent: Event dates are empty
          NoQuestionsDefined: There are no questions available
        """

        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.event = event
        logger.debug("Creating form for %s" % event)

        if event.start_date is None or event.end_date is None or \
           event.end_date < event.start_date:
            msg = "Dates for this event are wrong: Start: {}, "\
                  " End: {}".format(event.start_date, event.end_date)
            logger.critical(msg)
            raise NoStartDateEndDateEvent(msg)

        if not models.QuestionsDay.objects.exists() and\
           not models.QuestionsEvent.objects.exists() and\
           not models.QuestionsUser.objects.exists():
           msg = "No questions enabled."
           logger.critical(msg)
           raise NoQuestionsDefined(msg)

        self._create_fields_dates(event)
        self._create_fields_users(event)
        self._create_fields_event(event)

    def save(self, *args, **kwargs):
        """ Saving the form data into all models
        """
        logger.debug("Saving form data to models. Event id:%s" % self.event.id)
        for key in self.cleaned_data.keys():
            logger.debug("Saving %s from form to model" % key)
            answer_text = self.cleaned_data[key]
            ksp = key.split('_')
            if 'questionuser' in key:
                question_id = ksp[2]
                user_id = ksp[1]
                self._save_answer_user(user_id, question_id, answer_text)
            elif 'questionday' in key:
                question_id = ksp[2]
                day = datetime.strptime(ksp[1], '%Y%m%d')
                self._save_answer_day(day, question_id, answer_text)
            elif 'questionevent' in key:
                question_id = ksp[1]
                self._save_answer_event(question_id, answer_text)


class AnswersForm(forms.ModelForm):

    def __init__(self, question_text, *args, **kwargs):
        super(AnswersForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = question_text
        self.fields['text'].widget.attrs['rows'] = 5


class AnswersDayForm(AnswersForm):

    class Meta:
        model = models.AnswersDay
        fields = ['text']


class AnswersUserForm(AnswersForm):

    class Meta:
        model = models.AnswersUser
        fields = ['text']


class AnswersEventForm(AnswersForm):

    class Meta:
        model = models.AnswersEvent
        fields = ['text']

