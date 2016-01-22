from django.shortcuts import render,redirect
from django.views.generic import TemplateView,RedirectView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404, HttpResponseNotFound,HttpResponse,JsonResponse

from django.contrib.auth import authenticate, login,logout

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Project imports
from forms import UserForm

# Configure logger
import logging
log = logging.getLogger(__name__)

# Create your views here.
class LoginView(View):
    """
    Provides users the ability to login
    """
    template_name='login.html'

    
    def get(self, request):
        context = {}
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = {}
            
        # Check form    
        user_form = UserForm(request.POST)
        if not user_form.is_valid():
            raise Http404('Form not valid')
        
        # Authenticate user        
        user = authenticate(username=user_form.data['username'], 
                            password=user_form.data['password'])
        if user is not None:
            if user.is_active:
                log.info("Logging in user " + user_form.data['username'])
                login(request, user)                
                return JsonResponse( user_form.data )

                
        return HttpResponse(status = 400)


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/login/'

    def get(self, request, *args, **kwargs):
        log.info("Calling logout")
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
  
    
class BaseView(TemplateView): 
    template_name='base.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(self.__class__, self).dispatch(request, *args, **kwargs)
     
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        log.info( "Calling BaseView :" + str(request.user.username) + ":" )    
        return super(TemplateView, self).render_to_response(context)
    
    
    
       