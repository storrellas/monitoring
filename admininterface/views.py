from django.shortcuts import render,redirect
from django.views.generic import TemplateView, RedirectView, ListView, DetailView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound,HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout

from django.utils.decorators import method_decorator
from django.db.models import Sum
from django.core.files.base import ContentFile

# Thrid-party libs
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

# Project imports
from forms import *
from models import *
from admin import EventCheckResource

# Configure logger
import logging
log = logging.getLogger(__name__)


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
            print user_form.errors
            return HttpResponseBadRequest(user_form.errors)             
        
        log.info("Logging in " + user_form.data['username'])
        
        # Authenticate user        
        user = authenticate(username=user_form.data['username'], 
                            password=user_form.data['password'])
        if user is not None:
            if user.is_active and (user.is_superuser or user.role == User.COMPANY):
                login(request, user)                
                return JsonResponse( user_form.data )

                
        return HttpResponseBadRequest()


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
    
    
    def get(self, request, *args, **kwargs):
        print request.user
        context = self.get_context_data()
        log.info( "Calling BaseView :" + str(request.user.username) + ":" )    
        return super(BaseView, self).render_to_response(context)
    



class AdminView( LoginRequiredMixin, SuperuserRequiredMixin, ListView ):
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
    queryset = User.objects.filter(is_superuser=False)
    context_object_name = 'event_user_list'
    
    def get_queryset(self):

        try:
            order_field = self.request.GET['order_field']
            search_data = self.request.GET['search_data']
        except:
            return self.queryset.order_by('id')

        # Filter by search_data
        queryset = self.queryset.filter(username__startswith=search_data).order_by('id')
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
            
    
class EventView( LoginRequiredMixin, SuperuserRequiredMixin, ListView ):
    template_name='manage/event_list.html'
    model = Event
    paginate_by = 10
    context_object_name = 'event_list'
    queryset = Event.objects.all().order_by('id')

            
class EventAddView( LoginRequiredMixin, SuperuserRequiredMixin, TemplateView ):
    template_name='manage/addevent.html'
    model = Event
    
    def get_context_data(self, **kwargs):
        context = super(EventAddView, self).get_context_data(**kwargs)
      
        context['user_list'] = User.objects.filter(eventuser__event__isnull=True,
                                                   is_superuser=False)
        #context['user_list'] = User.objects.filter(is_superuser=False)        
        return context
    
    def post(self,request,*args,**kwargs):
        form = EventModelForm(request.POST, request.FILES)        
        if not form.is_valid():
            #raise Http404()          
            print form.errors
            return HttpResponseBadRequest(form.errors)
                
        # Save the form        
        event = form.save()      
        if request.POST['selno'] != '':            
            selno_list = str(request.POST['selno']).split(',')
            for id in selno_list:
                user = User.objects.get(id=int(id))
                eventuser = EventUser.objects.get(user=user)
                eventuser.event = event        
                eventuser.save()
        
        
        return redirect(reverse('event'))
    
class EventEditView( LoginRequiredMixin, SuperuserRequiredMixin, DetailView ):
    template_name='manage/editevent.html'
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        
        event = kwargs['object']
        eventuser_list = event.user.all()
        context['eventuser_list'] = eventuser_list
        context['user_list'] = User.objects.filter(event__isnull=True,
                                                   is_superuser=False)                
        context['selno'] = str(eventuser_list.values_list('id', flat=True))[1:-1]      
        return context
    
    def post(self,request,*args,**kwargs):
        log.info('Accessing form')

        event = Event.objects.get(id=kwargs['pk'])
        
        form = EventModelForm(request.POST, request.FILES, instance=event)        
        if not form.is_valid():
            #raise Http404()          
            print form.errors
            return HttpResponseBadRequest(form.errors)

        # Save form
        event = form.save()

        # Remove previous event users
        for eventuser in event.eventuser_set.all():            
            eventuser.event = None
            eventuser.save()

        # Add new EventUsers
        if request.POST['selno'] != '':            
            selno_list = str(request.POST['selno']).split(',')
            for id in selno_list:
                user = User.objects.get(id=int(id))
                eventuser = EventUser.objects.get(user=user)
                eventuser.event = event        
                eventuser.save()

        
        return redirect(reverse('event'))


class EventResultView( LoginRequiredMixin, ListView ):
    template_name='home/event_result.html'
    model = EventCheck
    paginate_by = 10
    context_object_name = 'eventcheck_list'
    event = None
    
    def get_queryset(self):
                    
        # An event was selected
        if 'event_id' in self.request.GET.keys():
            event_id = self.request.GET['eventid']
            self.event = Event.objects.get( id = event_id )            
        else:
            if self.request.user.is_superuser == True:
                self.event = Event.objects.first()
            else:
                self.event = Event.objects.filter(user=self.request.user).first()          
        return self.model.objects.filter(event=self.event).order_by('id')
    
    def get_context_data(self, **kwargs):
        context = super(EventResultView, self).get_context_data(**kwargs)
        if request.user.is_superuser:
            context['event_list'] = Event.objects.all()
        else:
            context['event_list'] = Event.objects.filter(user=self.request.user)
        

        analytics = EventCheck.objects.filter(event=self.event) \
                        .aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['target']*100 / context['sampling']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'
        context['eventid_selected'] = self.event.id

        return context

class EventAnalysisView( LoginRequiredMixin, TemplateView ):
    template_name='home/event_analysis.html'    
    
    def get_context_data(self, **kwargs):
        context = super(EventAnalysisView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['event_list'] = Event.objects.all()
        else:
            context['event_list'] = Event.objects.filter(user=self.request.user)

        
        # An event was selected
        if 'event_id' in self.request.GET.keys():
            event_id = self.request.GET['eventid']
            event = Event.objects.get( id = event_id )            
        else:
            if self.request.user.is_superuser == True:
                event = Event.objects.first()
            else:
                event = Event.objects.filter(user=self.request.user).first()

        # There are no event currently
        if event is None:
            context['eventid_selected'] = 0
            return context
        
        # Capture data for event_header.html
        eventcheck_list = EventCheck.objects.filter(event=event) 
        analytics = eventcheck_list.aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['target']*100 / context['sampling']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'
        context['eventid_selected'] = event.id

        
        # Add data for feedback graph
        feedback = {}
        feedback['Good'] = eventcheck_list.filter(type=EventCheck.GOOD).count()
        feedback['Neutral'] = eventcheck_list.filter(type=EventCheck.NEUTRAL).count()
        feedback['Bad'] = eventcheck_list.filter(type=EventCheck.BAD).count()
        context['feedback'] = feedback

        # Generate graph data
        graph_data = eventcheck_list.values('trackdate') \
                     .annotate(quantity = Sum('quantity'), target = Sum('target') )
        #print graph_data
        context['graph_data'] = graph_data


        return context

class EventResultCSVView( LoginRequiredMixin, View ):
    
    def get(self,request,*args,**kwargs):
        file_to_send = ContentFile(EventCheckResource().export().csv)
        response     = HttpResponse(file_to_send,'text/csv')
        response['Content-Length']      = file_to_send.size    
        response['Content-Disposition'] = 'attachment; filename="event.csv"'        
        return response

class ChangePwdView(LoginRequiredMixin, TemplateView):
    template_name='settings/changepwd.html'
    form = UserForm
    model = User
    queryset = User.objects.filter(is_superuser=True)
         
    def get_context_data(self, **kwargs):
        context = super(ChangePwdView, self).get_context_data(**kwargs)
        context['userid'] = self.request.user.id
        return context
