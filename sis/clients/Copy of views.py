from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms.models import formset_factory
from django.views.generic import CreateView

from braces.views import LoginRequiredMixin

from .forms import ClientCreateForm, AddressCreateForm, AddressFormSet, PhoneFormSet

# Import the customized User model
from .models import Client

import datetime

# Create your views here.

@login_required
def list(request):
    return render(request, 'clients/list.html')


class ClientCreateView(LoginRequiredMixin, CreateView):
    template_name = 'clients/create.html'
    model = Client
    form_class = ClientCreateForm
    success_url = 'success/'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        address_form = AddressFormSet()
        phone_form = PhoneFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  address_form=address_form,
                                  phone_form=phone_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        address_form = AddressFormSet(self.request.POST)
        phone_form = PhoneFormSet(self.request.POST)
        if (form.is_valid() and address_form.is_valid() and
            phone_form.is_valid()):
            return self.form_valid(form, address_form, phone_form)
        else:
            return self.form_invalid(form, address_form, phone_form)

    def form_valid(self, form, address_form, phone_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        form.instance.create_date = datetime.datetime.now
        form.instance.created_by = self.request.user
        address_form.instance = self.object
        address_form.save()
        phone_form.instance = self.object
        phone_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, address_form, phone_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  address_form=address_form,
                                  phone_form=phone_form))
        
        
#===============================================================================
# def create(request):
#     if request.method == 'POST':
#         form = ClientCreateForm(request.POST)
#         AddressFormset = formset_factory(AddressCreateForm)
#         formset = AddressFormset()
#         if form.is_valid():
#             client = form.save(commit=False)
#             client.status=Client.PENDING
#             client.save()
#             
#             return redirect('/clients/')
#     else:
#         form = ClientCreateForm()
#         AddressFormset = formset_factory(AddressCreateForm, extra=2,max_num=1)
#         formset = AddressFormset(initial=[
#                 {'prov': u'Qc',
#                 'city': u'Montreal',}
#         ])
#         
#     return render(request, 'clients/create.html', {'form': form, 'formset': formset})
#===============================================================================
