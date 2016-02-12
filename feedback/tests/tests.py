
from django.core.urlresolvers import reverse

from feedback.tests.feedbacktest import FeedbackTest
from feedback.exceptions import NoStartDateEndDateEvent
from feedback import views

class ClientsTestCase(FeedbackTest):

    def test_event_dates_empty(self):
        url = reverse("designfeedback", args=(1,))
        request = self.factory.get(url)
        with self.assertRaises(NoStartDateEndDateEvent):
            views.FeedBack.as_view()(request, 1)

    # def test_form_get_load(self):
    #     pass

    # def test_form_post_load(self):
    #     pass

    # def test_form_save_no_data(self):
    #     pass

    # def test_form_big_data(self):
    #     pass