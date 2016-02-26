from django.shortcuts import render,redirect
from django.views.generic import TemplateView, RedirectView, ListView, DetailView
from django.views.generic import FormView, UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateResponseMixin
from django.core.urlresolvers import reverse,reverse_lazy
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound,HttpResponse,JsonResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.forms.utils import ErrorList

from django.utils.decorators import method_decorator
from django.db.models import Sum, Q
from django.core.files.base import ContentFile

# Thrid-party libs
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from rest_framework.authtoken.models import Token

# Project imports
from forms import *
from models import *
from admin import EventCheckResource
from import_export import resources
from feedback.models import FeedbackList

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
                
        # Authenticate user        
        user = authenticate(username=user_form.data['username'], 
                            password=user_form.data['password'])
        if user is not None:
            if user.is_active and (user.is_superuser or user.role == User.COMPANY or user.role == User.SUPERVISOR):
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
    
class CompanyView( LoginRequiredMixin, SuperuserRequiredMixin, ListView ):
    template_name='manage/company_list.html'  
    model = User
    paginate_by = 10
    queryset = User.objects.filter(role=User.COMPANY).order_by('id')
    context_object_name = 'company_list'
    
    
    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)        
        context['event_list'] = Event.objects.all()        
        return context

class EventUserView( CompanyView ):    
    template_name = 'manage/eventuser_list.html'
    queryset = User.objects.filter(role=User.EVENTUSER)
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
        context['list_supervisors'] = User.objects.filter(role=User.SUPERVISOR)
        context['form'] = EventUserModelForm()
        return context

class EventSupervisorView(CompanyView):
    template_name='manage/supervisor_list.html'
    queryset = User.objects.filter(role=User.SUPERVISOR)
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
        context = super(EventSupervisorView, self).get_context_data(**kwargs)
        try:
            context['sortMode'] = self.request.GET['order_field']
        except:
            context['sortMode'] = 'ASC'
        try:
            context['search_data'] = self.request.GET['search_data']
        except:
            context['search_data'] = ''
        context['form'] = EventUserModelForm()
        return context

class EventUserAddView( LoginRequiredMixin, SuperuserRequiredMixin, CreateView ):
    template_name = "manage/eventuser_list.html"

    def post(self, request):
        """Stores the data, redirects to the list of Supervisors. Not using
        UpdateView as it does not fit with modals
        """
        form = EventUserModelForm(request.POST)
        if form.is_valid():
            log.debug("Form is valid")
            u = form.save()
            user = User.objects.get(username=u)
            user.role = User.EVENTUSER
            if request.FILES:
                user.picture = request.FILES['picture']
            id_supervisor = request.POST.get('eventuser')
            user.eventuser = User.objects.get(id=id_supervisor)
            # QUICK HACK
            # If we specify the fields password in the form, we modify the user
            # password. We should do this operation in the User model but it
            # required too many changes.
            password1 = request.POST.get("password")
            password2 = request.POST.get("password_confirm")
            if password1 != "" and password1 == password2:
                # This is too weak password check
                #   - Check length and charts
                #   - Do not let spaces
                user.set_password(password1)
                
                log.debug("Password for user `{}` changed to {}"
                          .format(user.username, ''.join(["*" for el in range(0,5)])))
                r = "0"
            elif password1 != "" and password1 != password2:
                r = "2"
            else:
                r = "0"
            user.save()
            Token.objects.create(user=user)
        else:
            log.debug("Form is invalid")
            log.debug(form.errors)
            r = "1&m={}".format(form.errors.as_text())

        return redirect("{}?r={}".format(reverse('user_list'), r))

class EventSupervisorAddView( LoginRequiredMixin, SuperuserRequiredMixin, TemplateView ):
    template_name = "manage/supervisor_list.html"

    def post(self, request):
        """Stores the data, redirects to the list of Supervisors. Not using
        UpdateView as it does not fit with modals
        """
        form = EventUserModelForm(request.POST)
        if form.is_valid():
            log.debug("Form is valid")
            u = form.save()
            user = User.objects.get(username=u)
            user.role = User.SUPERVISOR
            # QUICK HACK
            # If we specify the fields password in the form, we modify the user
            # password. We should do this operation in the User model but it
            # required too many changes.
            password1 = request.POST.get("password")
            password2 = request.POST.get("password_confirm")
            if password1 != "" and password1 == password2:
                # This is too weak password check
                #   - Check length and charts
                #   - Do not let spaces
                user.set_password(password1)
                
                log.debug("Password for user `{}` changed to {}"
                          .format(user.username, ''.join(["*" for el in range(0,5)])))
                r = "0"
            elif password1 != "" and password1 != password2:
                r = "2"
            else:
                r = "0"
            user.save()
        else:
            log.debug("Form is invalid")
            log.debug(form.errors)
            r = "1&m={}".format(form.errors.as_text())

        return redirect("{}?r={}".format(reverse('super_url'), r))

class EventUserEditView( LoginRequiredMixin, SuperuserRequiredMixin, TemplateView ):
    template_name = "manage/eventuser_list.html"

    def post(self, request, pk):
        """Stores the data, redirects to the list of Supervisors. Not using
        UpdateView as it does not fit with modals
        """
        user = User.objects.get(id=pk)
        form = EventUserModelForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            log.debug("Form is valid")
            form.save()
            if request.FILES:
                user.picture = request.FILES['picture']
            # QUICK HACK
            # If we specify the fields password in the form, we modify the user
            # password. We should do this operation in the User model but it
            # required too many changes.
            password1 = request.POST.get("password")
            password2 = request.POST.get("password_confirm")
            if password1 != "" and password1 == password2:
                # This is too weak password check
                #   - Check length and charts
                #   - Do not let spaces
                user.set_password(password1)
                user.save()
                log.debug("Password for user `{}` changed to {}"
                          .format(user.username, ''.join(["*" for el in range(0,5)])))
                r = "0"
            elif password1 != "" and password1 != password2:
                r = "2"
            else:
                r = "0"
                user.save()
        else:
            log.debug("Form is invalid")
            log.debug(form.errors)
            r = "1&m={}".format(form.errors.as_text())

        return redirect("{}?r={}".format(reverse('user_list'), r))

class UserDeleteView( LoginRequiredMixin, SuperuserRequiredMixin, DeleteView ):
    model = User
    success_url = reverse_lazy('home')

class EventSupervisorEditView( LoginRequiredMixin, SuperuserRequiredMixin, TemplateView ):
    template_name = "manage/supervisor_list.html"

    def post(self, request, pk):
        """Stores the data, redirects to the list of Supervisors. Not using
        UpdateView as it does not fit with modals
        """
        context_data = dict()
        user = User.objects.get(id=pk)
        form = EventUserModelForm(request.POST, instance=user,
                                  error_class=DivErrorList)
        if form.is_valid():
            log.debug("Form is valid")
            form.save()
            # QUICK HACK
            # If we specify the fields password in the form, we modify the user
            # password. We should do this operation in the User model but it
            # required too many changes.
            password1 = request.POST.get("password")
            password2 = request.POST.get("password_confirm")
            if password1 != "" and password1 == password2:
                # This is too weak password check
                #   - Check length and charts
                #   - Do not let spaces
                user.set_password(password1)
                user.save()
                log.debug("Password for user `{}` changed to {}"
                          .format(user.username, ''.join(["*" for el in range(0,5)])))
                r = "0"
            elif password1 != "" and password1 != password2:
                r = "2"
            else:
                r = "0"
        else:
            log.debug("Form is invalid")
            log.debug(form.errors)
            r = "1&m={}".format(form.errors.as_text())
        return redirect("{}?r={}".format(reverse('super_url'), r))

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
      
        context['user_list'] = User.objects.filter(event__isnull=True, role=User.EVENTUSER,
                                                   is_superuser=False).order_by('id')
        context['company_list'] = User.objects.filter(role=User.COMPANY).order_by('id')
        context['form'] = EventModelForm()
        context['location_list'] = Location.objects.all()
        return context
    
    def post(self,request,*args,**kwargs):        

        form = EventModelForm(request.POST, request.FILES)        
        if not form.is_valid():
            return HttpResponseBadRequest(form.errors)
                
        # Save the form        
        event = form.save()  

        # Add locations to event
        event.location.clear()
        if request.POST['sellocation'] != '':            
            sellocation_list = str(request.POST['sellocation']).split(',')
            for id in sellocation_list:
                location = Location.objects.get(id=int(id))
                event.location.add(location)
        
        # Add users to event
        event.user.clear()
        company = User.objects.get(id=request.POST['company'])
        event.user.add(company)
        if request.POST['selno'] != '':            
            selno_list = str(request.POST['selno']).split(',')
            for id in selno_list:
                user = User.objects.get(id=int(id))
                event.user.add(user)
                
        return redirect(reverse('event'))

class EventEditView( LoginRequiredMixin, SuperuserRequiredMixin, DetailView ):
    template_name='manage/editevent.html'
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        
        event = kwargs['object']
        eventuser_list = event.user.filter(role=User.EVENTUSER).order_by('id')
        context['eventuser_list'] = eventuser_list
        context['user_list'] = User.objects.filter(event__isnull=True, role=User.EVENTUSER,
                                                   is_superuser=False).order_by('id')                
        context['selno'] = str(eventuser_list.values_list('id', flat=True))[1:-1]
        context['company_list'] = User.objects.filter(role=User.COMPANY).order_by('id')
        context['form'] = EventModelForm()
        context['location_list'] = Location.objects.all()
        return context
    
    def post(self,request,*args,**kwargs):

        event = Event.objects.get(id=kwargs['pk'])
        form = EventModelForm(request.POST, request.FILES, instance=event)
        if not form.is_valid():
            #raise Http404()          
            print form.errors
            return HttpResponseBadRequest(form.errors)

        # Save form
        event = form.save()

        # Add locations to event
        event.location.clear()
        if request.POST['sellocation'] !=  '':            
            sellocation_list = str(request.POST['sellocation']).split(',')
            for id in sellocation_list:
                location = Location.objects.get(id=int(id))
                event.location.add(location)

        # Add users to event
        event.user.clear()
        company = User.objects.get(id=request.POST['company'])
        event.user.add(company)
        if request.POST['selno'] != '':            
            selno_list = str(request.POST['selno']).split(',')
            for id in selno_list:
                log.info('Adding user to event' + str(id))
                user = User.objects.get(id=int(id))
                event.user.add(user)
        
        return redirect(reverse('event'))

class EventResultView( LoginRequiredMixin, ListView ):
    template_name='home/event_result.html'
    model = EventCheck
    paginate_by = 10
    context_object_name = 'eventcheck_list'
    event = None
    
    def get_queryset(self):
           
        # An event was selected
        if 'eventid' in self.request.GET.keys():
            event_id = self.request.GET['eventid']
            self.event = Event.objects.get( id = event_id )
        else:
            if self.request.user.is_superuser == True:
                self.event = Event.objects.first()
            else:
                self.event = Event.objects.filter(user=self.request.user).first()          
        return self.model.objects.filter(event=self.event, completeflag=True).order_by('id')
    
    def get_context_data(self, **kwargs):
        context = super(EventResultView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['event_list'] = Event.objects.all()

        else:
            context['event_list'] = Event.objects.filter(user=self.request.user)
        

        analytics = EventCheck.objects.filter(event=self.event, completeflag=True) \
                        .aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['target']*100 / context['sampling']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'

        if self.event is not None:
            context['eventid_selected'] = self.event.id
            context['user_view_feedback'] = self.request.user in self.event.getSupervisors()


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
        if 'eventid' in self.request.GET.keys():
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
        eventcheck_list = EventCheck.objects.filter(event=event, completeflag=True) 
        analytics = eventcheck_list.aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['target']*100 / context['sampling']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'

        context['user_view_feedback'] = self.request.user in event.getSupervisors()
        context['eventid_selected']   = event.id


        good_quantity    = eventcheck_list.filter(type=EventCheck.GOOD).aggregate(good=Sum('quantity'))['good']
        neutral_quantity = eventcheck_list.filter(type=EventCheck.NEUTRAL).aggregate(neutral=Sum('quantity'))['neutral']
        bad_quantity     = eventcheck_list.filter(type=EventCheck.BAD).aggregate(bad=Sum('quantity'))['bad']
        total_quantity   = eventcheck_list.aggregate(total=Sum('quantity'))['total']        
        good_quantity    = int(good_quantity or 0)
        neutral_quantity = int(neutral_quantity or 0)
        bad_quantity     = int(bad_quantity or 0)
        total_quantity   = int(total_quantity or 1)

        
        # Add data for feedback graph
        feedback = {}
        try: #bug
            feedback['Good']    = (good_quantity*100)/total_quantity
            feedback['Neutral'] = (neutral_quantity*100)/total_quantity
            feedback['Bad']     = (bad_quantity*100)/total_quantity        
        except:
            feedback['Good']    = 99
            feedback['Neutral'] = 999
            feedback['Bad']     = 999
        context['feedback'] = feedback

        # Generate graph data
        graph_data = eventcheck_list.values('trackdate') \
                     .annotate(quantity = Sum('quantity'), target = Sum('target') )

        context['graph_data'] = graph_data

        return context

class ExportToCSV(LoginRequiredMixin, View):

    def getResponseCSV(self, resource, filename):
        """ Exports a resource to CSV. Generated CSV will be named as filename.
        Attributes:
          resource (resources.ModelResource or (callable, attribute) )
          filename: Name to be used on the exported csv file
        """
        if isinstance(resource, resources.ModelResource):
            content = resource.export().csv
        else:
            # Custom callable to export csv data, using the attribute
            content = resource[0](resource[1])
        file_to_send = ContentFile(content)

        response     = HttpResponse(file_to_send,'text/csv')
        response['Content-Length']      = file_to_send.size    
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename
        return response

class EventResultCSVView(ExportToCSV):

    def get(self,request, pk, *args,**kwargs):
        event = Event.objects.get(id=pk)
        filename = event.title.strip()
        return self.getResponseCSV(EventCheckResource(), filename)

class FeedbackCSVView(ExportToCSV):
    
    def get(self, request, *args, **kwargs):
        events = Event.objects.all()
        return self.getResponseCSV((FeedbackList.objects.toCSV, (events)), 'feedback')

class EventPicturesView( LoginRequiredMixin, ListView ):
    template_name='home/event_pictures.html'
    model = EventCheckImage
    context_object_name = 'eventcheckimage_list'
    
    def get_queryset(self):            
        # An event was selected
        if 'eventid' in self.request.GET.keys():
            event_id = self.request.GET['eventid']
            self.event = Event.objects.get( id = event_id )
        else:
            if self.request.user.is_superuser == True:
                self.event = Event.objects.first()
            else:
                self.event = Event.objects.filter(user=self.request.user).first()          
        return self.model.objects.filter(eventcheck__event=self.event).order_by('id')

    
    def get_context_data(self, **kwargs):
        context = super(EventPicturesView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['event_list'] = Event.objects.all()
        else:
            context['event_list'] = Event.objects.filter(user=self.request.user)
        
        # An event was selected
        if 'eventid' in self.request.GET.keys():           
            event_id = self.request.GET['eventid']
            event = Event.objects.get( id = event_id )            
        else:            
            if self.request.user.is_superuser == True:
                event = Event.objects.first()
            else:
                event = Event.objects.filter(user=self.request.user).first()

        analytics = EventCheck.objects.filter(event=event, completeflag=True) \
                        .aggregate(Sum('quantity'), Sum('target'))
        try:
            context['sampling']    = analytics['quantity__sum']
            context['target']      = analytics['target__sum']
            context['percentage']  = str(context['target']*100 / context['sampling']) + '%' 
        except:
            context['sampling']    = '0'
            context['target']      = '0'
            context['percentage']  = '0%'
        if event is not None:
            context['eventid_selected'] = self.event.id

        return context

class ChangePwdView(LoginRequiredMixin, TemplateView):
    template_name='settings/changepwd.html'
    form = UserForm
    model = User
    queryset = User.objects.filter(is_superuser=True)
         
    def get_context_data(self, **kwargs):
        context = super(ChangePwdView, self).get_context_data(**kwargs)
        context['userid'] = self.request.user.id
        return context
    
class ProductView( LoginRequiredMixin, ListView ):
    template_name='manage/product_list.html'
    model = Product
    paginate_by = 10
    context_object_name = 'product_list'
    queryset = Product.objects.all().order_by('id')
    
    def get_queryset(self):
                    
        try:
            order_field = self.request.GET['order_field']
            search_data = self.request.GET['search_data']
        except:
            return self.queryset.order_by('id')

        # Filter by search_data
        queryset = self.queryset.filter(name__startswith=search_data).order_by('id')
        if order_field == 'ASC':
            return queryset.order_by('name').order_by('id')
        else:
            return queryset.order_by('name').order_by('id') 
        
class LocationView( LoginRequiredMixin, ListView ):
    template_name='manage/location_list.html'
    model = Location
    paginate_by = 10
    context_object_name = 'location_list'
    queryset = Location.objects.all().order_by('id')
    
    def get_queryset(self):
                    
        try:
            order_field = self.request.GET['order_field']
            search_data = self.request.GET['search_data']
        except:
            return self.queryset.order_by('id')

        # Filter by search_data
        queryset = self.queryset.filter(name__startswith=search_data).order_by('id')
        if order_field == 'ASC':
            return queryset.order_by('name').order_by('id')
        else:
            return queryset.order_by('name').order_by('id') 

class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    success_url = reverse_lazy('location')


