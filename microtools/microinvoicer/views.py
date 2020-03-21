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

class MicroHomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            db = self.request.user.load_datastore()
        else:
            db = micro_models.fake_anonymous_data()

        context['seller'] = { 'name' : db.register.seller.name }
        context['invoices'] = db.register.invoices
        return context


class MicroRegistrationView(RegistrationView):
    template_name = 'registration_form.html'
    form_class = forms.MicroRegistrationForm
    # For now, we redirect straight to fiscal information view after signup.
    # When we'll change to two step registration, fiscal form will be shown at
    # the first login
    success_url = reverse_lazy('microinvoice_fiscal_entity')


class MicroLoginView(LoginView):
    template_name = 'login.html'


class BaseFormView(LoginRequiredMixin, FormView):
    """Extend this view for any form"""
    template_name = 'base_form.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class SellerView(BaseFormView):
    """
    Updates user's fiscal information.
    ATTENTION: any previous user data will be erased
    """
    form_title = 'Setup fiscal information'
    form_class = forms.SellerForm

    def form_valid(self, form):
        invoice_series = form.cleaned_data.pop('invoice_series')
        start_no = form.cleaned_data.pop('start_no')
        seller = models.FiscalEntity(**form.cleaned_data)
        # TODO: factor this out of the view
        # create empty registry
        registry = models.InvoiceRegister(seller=seller, invoice_series=invoice_series, next_number=start_no)
        db = models.LocalStorage(registry)
        form.user.save_datastore(db)

        return super().form_valid(form)

class BuyerView(BaseFormView):
    """Updates buyer and contract details"""
    form_title = 'Buyer contract details'
    form_class = forms.BuyerForm

    def form_valid(self, form):
        hourly_rate = form.cleaned_data.pop('hourly_rate')
        buyer = models.FiscalEntity(**form.cleaned_data)
        contract = models.ServiceContract(buyer=buyer, hourly_rate=hourly_rate)

        # TODO: factor this out of the view
        db = form.user.load_datastore()
        db.contracts.append(contract)
        form.user.save_datastore(db)

        return super().form_valid(form)


class ContractsView(LoginRequiredMixin, ListView):
    template_name = 'contract_list.html'

    def get_queryset(self):
        db = self.request.user.load_datastore()
        return db.contracts


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
