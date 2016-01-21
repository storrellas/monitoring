from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

# Configure logger
import logging
log = logging.getLogger(__name__)

# Create your views here.
class LoginView(TemplateView):
    template_name='login.html'
    
    def get(self, request, *args, **kwargs):                
        context = self.get_context_data()
        log.info( "Calling Loginview" )

        return super(TemplateView, self).render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        log.info( "Calling Loginview with post" )
        #return super(TemplateView, self).render_to_response(context)
        return redirect( reverse('base') )