from django.shortcuts import render,redirect
from django.views.generic import TemplateView, RedirectView, ListView, DetailView
from django.views.generic.base import TemplateResponseMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404, HttpResponseNotFound,HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Django braces
from braces.views import LoginRequiredMixin

# Project imports
from forms import UserForm
from api.models import *

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
        
        log.info("Logging in " + user_form.data['username'])
        log.info("Logging in " + user_form.data['username'])
        
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
    
class BaseView( LoginRequiredMixin, TemplateView ): 
    template_name='base.html'
    
    """
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        log.info( "Calling BaseView :" + str(request.user.username) + ":" )    
        return super(BaseView, self).render_to_response(context)
    """



class AdminView( LoginRequiredMixin, ListView ):
    template_name='manage/admin_list.html'  
    model = User
    paginate_by = 10
    queryset = User.objects.filter(is_superuser=True).order_by('id')
    context_object_name = 'admin_list'
    
    
    #def get_queryset(self):
    #    return User.objects.filter(is_superuser=True).order_by('id')    
    
    def get_context_data(self, **kwargs):
        context = super(AdminView, self).get_context_data(**kwargs)        
        context['event_list'] = Event.objects.all()        
        return context
   

class EventUserView( AdminView ):    
    template_name='manage/user_list.html'  
    queryset = User.objects.filter(is_superuser=False).order_by('id')
    context_object_name = 'event_user_list'
    
    def get_queryset(self):

        try:
            order_field = self.request.GET['order_field']
            search_data = self.request.GET['search_data']
        except:
            return self.queryset.order_by('username')

        # Filter by search_data
        queryset = self.queryset.filter(username__startswith=search_data)
        if order_field == 'ASC':
            return queryset.order_by('username')
        else:
            return queryset.order_by('username')       
    
    def get_context_data(self, **kwargs):
        context = super(EventUserView, self).get_context_data(**kwargs)                        
        try:
            context['sortMode'] = self.request.GET['order_field']
        except: 
            context['sortMode'] = 'ASC'
        try:
            context['search_data'] = self.request.GET['search_data']
        except: 
            context['search_data'] = ''                                         
        return context    
            
    
class EventView( LoginRequiredMixin, ListView ):
    template_name='manage/event_list.html'
    model = Event
    paginate_by = 10
    context_object_name = 'event_list'
    
class EventEditView( LoginRequiredMixin, DetailView ):
    template_name='manage/editevent.html'
    model = Event
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super(EventUserView, self).get_context_data(**kwargs)                            
        context['user_list'] = self.request.GET['search_data']
        return context    
    
         