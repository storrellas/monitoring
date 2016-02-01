from django.shortcuts import render,redirect
from django.views.generic import TemplateView, RedirectView, ListView, DetailView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound,HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.files.base import ContentFile

# Thrid-party libs
from braces.views import LoginRequiredMixin

# Project imports
from forms import *
from api.models import *
from api.admin import TrackDataResource

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
            #raise Http404(event_form.errors)
            print user_form.errors
            return HttpResponseBadRequest(user_form.errors)             
        
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
            
    
class EventView( LoginRequiredMixin, ListView ):
    template_name='manage/event_list.html'
    model = Event
    paginate_by = 10
    context_object_name = 'event_list'
    queryset = Event.objects.all().order_by('id')

            
class EventAddView( LoginRequiredMixin, TemplateView ):
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
    
class EventEditView( LoginRequiredMixin, DetailView ):
    template_name='manage/editevent.html'
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        
        event = kwargs['object']
        eventuser_list = event.eventuser_set.all()
        context['eventuser_list'] = eventuser_list
        context['user_list'] = User.objects.filter(eventuser__event__isnull=True,
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

class EventAnalysisCSVView( LoginRequiredMixin, View ):
    
    def get(self,request,*args,**kwargs):
        file_to_send = ContentFile(TrackDataResource().export().csv)
        response     = HttpResponse(file_to_send,'text/csv')
        response['Content-Length']      = file_to_send.size    
        response['Content-Disposition'] = 'attachment; filename="event.csv"'        
        return response

class EventAnalysisView( LoginRequiredMixin, ListView ):
    template_name='home/event_analysis.html'
    model = TrackData
    paginate_by = 10
    context_object_name = 'trackdata_list'
    event = None
    
    def get_queryset(self):
        try:
            event_id = self.request.GET['eventid']            
        except:
            event_id = Event.objects.first().id
        self.event = Event.objects.get( id = event_id )
        
        return self.model.objects.filter(event=self.event).order_by('id')
    
    def get_context_data(self, **kwargs):
        context = super(EventAnalysisView, self).get_context_data(**kwargs)
        context['event_list'] = Event.objects.all()
        

        analytics = TrackData.objects.filter(event=self.event) \
                        .aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['sampling']*100 / context['target']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'
        context['eventid_selected'] = self.event.id

        return context



class EventResultView( LoginRequiredMixin, TemplateView ):
    template_name='home/event_result.html'

    
    
    def get_context_data(self, **kwargs):
        context = super(EventResultView, self).get_context_data(**kwargs)
        context['event_list'] = Event.objects.all()

        # Capture selected event
        try:
            event_id = self.request.GET['eventid']            
        except:
            event_id = Event.objects.first().id
        event = Event.objects.get( id = event_id )        

        # Capture data for event_header.html
        trackdata_list = TrackData.objects.filter(event=event) 
        analytics = trackdata_list.aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['sampling']*100 / context['target']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'
        context['eventid_selected'] = event.id

        
        # Add data for feedback graph
        feedback = {}
        feedback['Good'] = trackdata_list.filter(type=TrackData.GOOD).count()
        feedback['Neutral'] = trackdata_list.filter(type=TrackData.NEUTRAL).count()
        feedback['Bad'] = trackdata_list.filter(type=TrackData.BAD).count()
        context['feedback'] = feedback

        # Generate graph data
        graph_data = trackdata_list.values('trackdate') \
                     .annotate(quantity = Sum('quantity'), target = Sum('target') )
        #print graph_data
        context['graph_data'] = graph_data

        return context


        
         