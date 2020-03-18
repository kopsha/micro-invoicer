from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django_registration.backends.one_step.views import RegistrationView

from . import forms


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

class FiscalEntityView(LoginRequiredMixin, FormView):
    form_title = 'Setup your fiscal information'
    template_name = 'base_form.html'
    form_class = forms.FiscalEntityForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
