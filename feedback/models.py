from itertools import chain
from datetime import timedelta
from admininterface.models import Event, User
from django.db import models

# Defines the length of the questions and answers
LENGTH_QUESTIONS = 400
LENGTH_ANSWERS = 1000


class FeedbackDay(models.Model):
    """ Stores feedback per campaign per day.
    """
    event = models.ForeignKey(Event)
    day = models.DateField()

    class Meta:
        unique_together = ("event", "day")


class QuestionsManager(models.Manager):
    """ Model Manager to retrieve answer values
    """
    def getInitial(self, event, question, day=None, user=None):
        """ Gets the text value for an answer for the attributes
        """
        o = []
        if self.__str__() == "feedback.QuestionsDay.objects":
            d = FeedbackDay.objects.filter(event=event, day=day)
            if len(d):
                d = d[0]
                # Using the feedbackday to save the answer.
                o = AnswersDay.objects.filter(feedbackday=d, question=question)

        if self.__str__() == "feedback.QuestionsUser.objects":
            o = AnswersUser.objects.filter(user=user, question=question,
                                           event=event)

        if self.__str__() == "feedback.QuestionsEvent.objects":
            o = AnswersEvent.objects.filter(question=question, event=event)

        return "" if len(o) == 0 else o[0].text

    def exists(self):
        """ Returns True when there are questions enabled, False otherwise
        """
        return self.filter(enabled=True).count() > 0


class QuestionsDay(models.Model):
    """ Questions for each day on a campaign
    """
    text = models.CharField(max_length=LENGTH_QUESTIONS)
    enabled = models.BooleanField(default=True)

    objects = QuestionsManager()

    def full_sentence(self, day):
        """ Returns question + subject. On the form we display the question and
        the subject.
        Example, question='how are you' subject='2015/01/02'
        returns how are you (2015/01/02)
        """
        return u"{} ({})".format(self.text, day)

    def get_answer(self, event, day):
        """ Returns the answer for this question on the event passed by parameter.
        Returns None if there is no answer
        """
        try:
            return AnswersDay.objects.get(question=self,
                                          feedbackday__event=event,
                                          feedbackday__day=day).text
        except:
            return "No answer"

    def getCSVLine(self, event):
        """ Returns a CSV Line for this question for the event passed by
        parameter. The line returnes is of the format `Eventday, supervisor,
        Question, Answer\r\n`. If no answer, the line returned is of the format
        `,Question,No answer`
        """
        out = ""
        for day in event.getDays():
            answer = self.get_answer(event, day)
            answer = answer if answer is not None else "No answer"
            out = u"{}{},{},{},{}\r\n".format(out, event.title, '-',
                                              self.full_sentence(day),
                                              answer)
        return out

    def __unicode__(self):
        return unicode(self.text)


class AnswersDay(models.Model):
    """ Answers for a specific day on a campaign
    """
    question = models.ForeignKey(QuestionsDay)
    feedbackday = models.ForeignKey(FeedbackDay)
    text = models.TextField(max_length=LENGTH_ANSWERS, blank=True)

    class Meta:
        unique_together = ("question", "feedbackday")

    def getCSVLine(self):
        return ",{},{}".format(self.question.full_sentence(self.feedbackday.day),
                               self.text)


class QuestionsUser(models.Model):
    """ Questions for each user on a campaign
    """
    text = models.CharField(max_length=LENGTH_QUESTIONS)
    enabled = models.BooleanField(default=True)

    objects = QuestionsManager()

    def full_sentence(self, user):
        """ Returns question + subject. On the form we display the question and
        the subject.
        Example, question='how are you' subject='2015/01/02'
        returns how are you (2015/01/02)
        """
        username = user.username if user.get_full_name() == "" else user.get_full_name()
        return u"{} ({})".format(self.text, username)

    def get_answer(self, event, user):
        """ Returns the answer for this question on the event passed by parameter.
        Returns None if there is no answer
        """
        try:
            return AnswersUser.objects.get(question=self, event=event,
                                           user=user).text
        except AnswersUser.DoesNotExist:
            return "No answer"

    def getCSVLine(self, event):
        """ Returns a CSV Line for this question for the event passed by parameter.
        The line returnes is of the format `eventname,supervosr,Question,
        Answer\r\n`
        If no answer, the line returned is of the format `,Question,No answer`
        """
        out = ""
        for question in QuestionsUser.objects.filter(enabled=True):
            for user in event.user.all():
                answer = self.get_answer(event, user)
                answer = answer if answer is not None else "No answer"
                out = u"{}{},{},{},{}\r\n".format(out, event.title, '-',
                                                  question.full_sentence(user),
                                                  answer)
        return out

    def __unicode__(self):
        return self.text


class AnswersUser(models.Model):
    """ Answers for a user
    """
    user = models.ForeignKey(User)
    question = models.ForeignKey(QuestionsUser)
    event = models.ForeignKey(Event)
    text = models.TextField(max_length=LENGTH_ANSWERS, blank=True)

    class Meta:
        unique_together = ("user", "question", "event")

    def getCSVLine(self):
        return ",{},{}".format(self.question.full_sentence(self.user),
                               self.text)


class QuestionsEvent(models.Model):
    """ Questions on a campaign
    """
    text = models.CharField(max_length=LENGTH_QUESTIONS)
    enabled = models.BooleanField(default=True)

    objects = QuestionsManager()

    def full_sentence(self):
        """ Returns question + subject. On the form we display the question and
        the subject.
        Example, question='how are you' subject='2015/01/02'
        returns how are you (2015/01/02)
        """
        return unicode(self.text)

    def get_answer(self, event):
        """ Returns the answer for this question on the event passed by parameter.
        Returns None if there is no answer
        """
        try:
            return AnswersEvent.objects.get(question=self, event=event).text
        except AnswersEvent.DoesNotExist:
            return "No answer"

    def getCSVLine(self, event):
        """ Returns a CSV Line for this question for the event passed by parameter.
        The line returnes is of the format `Event name, supervisor,
        Question, Answer\r\n`
        If no answer, the line returned is of the format `,Question,No answer`
        """
        return u"{},{},{},{}\r\n".format(event.title, '-', self.text,
                                     self.get_answer(event))

    def __unicode__(self):
        return self.text


class AnswersEvent(models.Model):
    """ Answers on a campaign
    """
    question = models.ForeignKey(QuestionsEvent)
    event = models.ForeignKey(Event)
    text = models.TextField(max_length=LENGTH_ANSWERS, blank=True)

    class Meta:
        unique_together = ("event", "question")

    def getCSVLine(self):
        return ",{},{}".format(self.question.full_sentence(),
                               self.text)


class FeedbackManager(models.Manager):

    def toCSV(self, events):
        """ Custom method to export all feedback to CSV. We return a string
        containing all feedback.
        Attributes:

        """
        out = "Event,Supervisor,Question,Answer\r\n"
        # Generating content for AnswersUsers
        for event in events:
            questions = event.getQuestions()
            if len(questions) == 0:
                out = u"{},No questions defined".format(out)
            else:
                for question in questions:
                    out = u"{}{}".format(out, question.getCSVLine(event))
        return out


class FeedbackList(models.Model):

    objects = FeedbackManager()


def eventGetAnswers(self):
    """ Returns a list of all anwsers from feedback from the event contained
    in self
    """
    answersUsers = AnswersUser.objects.filter(event=self)
    answersDay = AnswersDay.objects.filter(feedbackday__event=self)
    answersEvent = AnswersEvent.objects.filter(event=self)
    return list(chain(answersUsers, answersDay, answersEvent))


def eventGetQuestions(self):
    """ Returns a list of all feedback questions
    in self
    """
    questionsUsers = QuestionsUser.objects.filter(enabled=True)
    questionsDay = QuestionsDay.objects.filter(enabled=True)
    questionsEvent = QuestionsEvent.objects.filter(enabled=True)
    return list(chain(questionsUsers, questionsDay, questionsEvent))


def getDaysCampaign(self):
    if self.end_date is not None and self.start_date is not None:
        num_days = (self.end_date.date() - self.start_date.date()).days+1
        for da in range(0, num_days):
            yield (self.start_date + timedelta(days=da)).date()

Event.getAnswers = eventGetAnswers
Event.getQuestions = eventGetQuestions
Event.getDays = getDaysCampaign
