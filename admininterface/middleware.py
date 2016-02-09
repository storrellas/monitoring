from django.core.urlresolvers import reverse
from django.http import Http404,HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser

from models import *

# Configure logger
import logging
log = logging.getLogger(__name__)


class CheckRole(object):

    def process_request(self, request):
        return None
