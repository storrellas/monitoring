import logging

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("django")


class FeedbackTest(TestCase):
    """Custom implementation for feedback of django.test.TestCase. All tests
    executed inherit from this class. We can modify the behaviour of all tests
    using this class.
    """
    fixtures = ['admininterface/fixtures/initial.json',
                'admininterface/fixtures/auth_token.json'
                ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()  # Petitions done on user Anonymous.

        logger.info("Executing test %s", self.id().split(".")[-1])
        logger.debug("Test description: %s", self.shortDescription())

    def tearDown(self):
        logger.info("Test finished.")
