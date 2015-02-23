import sys
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    #return render(request, 'core/home.html')
    return redirect('client_list')

# requires attribute ajax_template_name
class AjaxTemplateMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        print >>sys.stderr, '*** AjaxTemplateMixin - request.GET %s ****' % request.GET 
        if request.is_ajax():
            # test for module autocomplete-light
            # or ('_popup' in request.GET and request.GET['_popup'] == '1'):
            
            self.template_name = self.ajax_template_name
            print >>sys.stderr, '*** AjaxTemplateMixin - AJAX REQUEST %s ****' % self.template_name
        
        return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)

class ActionMixin(object):
    form_action_url = None
    
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
    
    def item_name(self):
        msg = "{0} is missing item_name.".format(self.__class__)
        raise NotImplementedError(msg)
        
    def get_form_action_url(self):
        if self.form_action_url:
            return self.form_action_url
        
        msg = "{0} is missing form_action_url.".format(self.__class__)
        raise NotImplementedError(msg)
    
    def form_valid(self, form):
        if self.action == 'create':
            msg = _('%s added.') % self.item_name
        else:
            msg = _('%s updated.') % self.item_name
            
        messages.info(self.request, msg)
        return super(ActionMixin, self).form_valid(form)
    
    def form_action(self):
        if self.action == 'create':
            return reverse_lazy(self.get_form_action_url())
        else:
            return reverse_lazy(self.get_form_action_url(), args=[str(self.object.id)])
        
    def form_title(self, form):
        if self.action == 'create':
            return _('%s registration.') % self.item_name
        else:
            return _('Contact update.') % self.item_name
        
            
class ModalMixin(object):
    target_modal_url_context_obj_name = ''
    target_modal_url=''
    
    def get_target_modal_url(self):
        if self.target_modal_url:
            return reverse_lazy(self.target_modal_url)
        
        msg = "{0} is missing target_modal_url.".format(self.__class__)
        raise NotImplementedError(msg)
    
    def get_target_modal_url_context_name(self):
        if self.target_modal_url_context_obj_name:
            return self.target_modal_url_context_obj_name
        
        msg = "{0} is missing target_modal_url_context_obj_name.".format(self.__class__)
        raise NotImplementedError(msg)
    
    def get_context_data(self, **kwargs):
        context = super(ModalMixin, self).get_context_data(**kwargs)
        context[self.get_target_modal_url_context_name()] = self.target_modal_url #self.get_target_modal_url()
        return context
    
class MultipleModalMixin(object):
    target_modals = {} # key = context object name -> value = target url name (as defined in urls.py)
    
    def get_target_modals(self):
        if self.target_modals:
            return self.target_modals
        msg = "{0} is missing target_modals.".format(self.__class__)
        raise NotImplementedError(msg)
    
    # override this methode to return an url that includes parameters
    def get_target_modal_url(self, context_url_object_name):
        url_name = self.get_target_modals().get(context_url_object_name)
        return reverse_lazy(url_name)
        
    def get_context_data(self, **kwargs):
        context = super(MultipleModalMixin, self).get_context_data(**kwargs)
        
        for context_object_name in self.get_target_modals().keys():
            target_url = self.get_target_modal_url(context_object_name)
            
            context[context_object_name] = target_url
            
        return context
    
    