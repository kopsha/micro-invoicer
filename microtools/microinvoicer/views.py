from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django_registration.backends.one_step.views import RegistrationView

from . import forms
from . import models

class MicroHomeView(TemplateView):
    template_name = 'index.html'


class MicroRegistrationView(RegistrationView):
    template_name = 'registration_form.html'
    form_class = forms.MicroRegistrationForm
    # For now, we redirect straight to fiscal information view after signup.
    # When we'll change to two step registration, fiscal form will be shown at
    # the first login
    success_url = reverse_lazy('microinvoice_fiscal_entity')


class MicroLoginView(LoginView):
    template_name = 'login.html'


class SellerView(LoginRequiredMixin, FormView):
    form_title = 'Setup your seller fiscal information'
    template_name = 'base_form.html'
    form_class = forms.SellerForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        return context

    def form_valid(self, form):
        invoice_series = form.cleaned_data.pop('invoice_series')
        start_no = form.cleaned_data.pop('start_no')
        seller = models.FiscalEntity(**form.cleaned_data)
        registry = models.InvoiceRegister(
            seller=seller,
            invoice_series=invoice_series,
            next_number=start_no
        )
        # save this shit to db
        print(registry)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'


class QuickView(TemplateView):
    template_name = 'quickview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # TODO: pick user data
            context['seller'] = { 'name' : 'BETTY SRL' }
            context['invoices'] = [
            {
                'series_number' : 'JUST-01',
                'buyer' : 'CLIENTUL S.R.L.',
                'duration' : 128,
                'value' : 106876.31,
            }]
        else:
            # TODO: factor this out someday
            context['seller'] = { 'name' : 'Anonymous' }
            context['invoices'] = [{
                'series_number' : 'A-0001',
                'buyer' : 'ANONYMOUS S.R.L.',
                'duration' : 128,
                'value' : 106876.31,
            },
            {
                'series_number' : 'A-0002',
                'buyer' : 'ANONYMOUS S.R.L.',
                'duration' : 92,
                'value' : 6995.12,
            }]
        print(context)
        return context
