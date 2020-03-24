from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django_registration.backends.one_step.views import RegistrationView

from . import forms
from . import models
from . import micro_models
from . import micro_use_cases as muc


class IndexView(TemplateView):
    template_name = 'index.html'


class MicroRegistrationView(RegistrationView):
    template_name = 'registration_form.html'
    form_class = forms.MicroRegistrationForm
    # For now, we redirect straight to fiscal information view after signup.
    # When we'll change to two step registration, fiscal form will be shown at
    # the first login
    success_url = reverse_lazy('microinvoicer_setup')


class MicroLoginView(LoginView):
    template_name = 'login.html'


class MicroHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            db = self.request.user.read_data()
            context['seller'] = { 'name' : db.register.seller.name }
            context['contracts'] = db.flatten_contracts()
            context['invoices'] = db.invoices()

        return context


class BaseFormView(LoginRequiredMixin, FormView):
    """Extend this view for any form"""
    template_name = 'base_form.html'
    success_url = reverse_lazy('microinvoicer_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class SellerView(BaseFormView):
    """Updates user's fiscal information.
    ATTENTION: any previous user data will be erased
    TODO: check if there was any data before
    """
    form_title = 'Setup fiscal information'
    form_class = forms.SellerForm

    def form_valid(self, form):
        names = form.cleaned_data['owner_fullname'].split(' ')
        form.user.last_name = names[-1]
        form.user.first_name = ' '.join(names[:-1])
        db = muc.create_empty_db(form.cleaned_data)
        form.user.write_data(db)
        return super().form_valid(form)


class ContractView(BaseFormView):
    """Contract details"""
    form_title = 'Buyer contract details'
    form_class = forms.ContractForm

    def form_valid(self, form):
        db = form.user['db']
        contract = muc.create_contract(form.cleaned_data)
        db.contracts.append(contract)
        self.request.user.write_data(db)
        return super().form_valid(form)


class ContractsView(LoginRequiredMixin, ListView):
    """Contracts manager"""
    template_name = 'contract_list.html'

    def get_queryset(self):
        db = self.request.user.read_data()
        return db.flatten_contracts()


class DraftInvoiceView(BaseFormView):
    """Creates a new draft invoice"""
    form_title = 'Generate new draft invoice'
    form_class = forms.InvoiceForm

    def form_valid(self, form):
        db = form.user['db']
        db = muc.draft_time_invoice(db, form.cleaned_data)
        self.request.user.write_data(db)
        return super().form_valid(form)


class ProfileView(BaseFormView):
    template_name = 'profile.html'
    form_title = 'Your Profile'
    form_class = forms.ProfileForm
