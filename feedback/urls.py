
from django.conf.urls import url

from feedback import views

urlpatterns = [

    url(r'^(?P<id>[0-9]+)$', views.FeedBack.as_view(),
        name='viewFeedbackForm'),
    url(r'^list/$', views.ListQuestions.as_view(),
        name='list_questions'),
    url(r'^delete_question/$', views.DeleteQuestion.as_view(),
        name='delete_question'),
]
