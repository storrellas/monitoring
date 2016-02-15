
from django.conf.urls import url

from feedback import views

urlpatterns = [

    url(r'^(?P<id>[0-9]+)$', views.FeedBack.as_view(),
        name='viewFeedbackForm')
]
