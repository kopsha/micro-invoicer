"""How about now."""

from django.http import Http404, FileResponse
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView, ListView
from django.views.generic.edit import FormView, DeletionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django_registration.backends.one_step.views import RegistrationView

from . import forms
from . import micro_use_cases as muc

from dataclasses import asdict, astuple


class IndexView(TemplateView):
    """Landing Page."""

    template_name = 'index.html'


class MicroRegistrationView(RegistrationView):
    """User registration."""

    template_name = 'registration_form.html'
    form_class = forms.MicroRegistrationForm
    # For now, we redirect straight to fiscal information view after signup.
    # When we'll change to two step registration, fiscal form will be shown at
    # the first login
    success_url = reverse_lazy('microinvoicer_setup')


class MicroLoginView(LoginView):
    """Classic login."""

    template_name = 'login.html'


class MicroHomeView(LoginRequiredMixin, TemplateView):
    """User Home."""

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """Attach all registry info."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            db = self.request.user.read_data()
            context['seller'] = {'name': db.register.seller.name}
            context['contracts'] = db.flatten_contracts()
            context['invoices'] = db.invoices()

        return context


class BaseFormView(LoginRequiredMixin, FormView):
    """Extend this view for any form."""

    template_name = 'base_form.html'
    success_url = reverse_lazy('microinvoicer_home')

    def get_context_data(self, **kwargs):
        """Add form title."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = self.form_title

        return context

    def get_form_kwargs(self):
        """Adds user information required for later validation."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class SellerView(BaseFormView):
    """
    Updates user's fiscal information.

    ATTENTION: any previous user data will be erased
    TODO: check if there was any data before
    """

    form_title = 'Setup fiscal information'
    form_class = forms.SellerForm

    def form_valid(self, form):
        """Scratch out user database."""
        db = muc.create_empty_db(form.cleaned_data)
        self.request.user.write_data(db)
        return super().form_valid(form)


class RegisterContractView(BaseFormView):
    """Add new contract to the registry."""

    form_title = 'Register new contract'
    form_class = forms.ContractForm

    def form_valid(self, form):
        """Just append, no biggie"""
        db = self.request.user.read_data()
        contract = muc.create_contract(form.cleaned_data)
        db.contracts.append(contract)
        self.request.user.write_data(db)
        return super().form_valid(form)


class ContractDetailsView(BaseFormView):
    """Amend contract details"""

    form_title = 'Contract details'
    form_class = forms.ContractForm
    template_name = 'base_details_form.html'

    def get_initial(self, **kwargs):
        """provide contract details using the url argument as index"""
        initial = super().get_initial()
        db = self.request.user.read_data()
        self.contract_ndx = None

        try:
            ndx = int(self.kwargs['contract_id']) - 1
            contract = db.contracts[ndx]
            initial['name'] = contract.buyer.name
            initial['owner_fullname'] = contract.buyer.owner_fullname
            initial['registration_id'] = contract.buyer.registration_id
            initial['fiscal_code'] = contract.buyer.fiscal_code
            initial['address'] = contract.buyer.address
            initial['bank_account'] = contract.buyer.bank_account
            initial['bank_name'] = contract.buyer.bank_name
            initial['registry_id'] = contract.registry_id
            initial['registry_date'] = contract.registry_date
            initial['hourly_rate'] = contract.hourly_rate
            self.contract_ndx = ndx

        except (IndexError, KeyError):
            raise Http404

        return initial

    def get_context_data(self, **kwargs):
        """Appends last invoice details to context data"""
        context = super().get_context_data(**kwargs)
        context['update_self_url'] = reverse_lazy(
            'microinvoicer_contract',
            kwargs={'contract_id': self.contract_ndx + 1}
        )
        return context

    def form_valid(self, form):
        """Something has changed, must update db."""
        assert self.contract_ndx is not None
        db = self.request.user.read_data()
        db.contracts[self.contract_ndx] = muc.create_contract(form.cleaned_data)
        self.request.user.write_data(db)
        return super().form_valid(form)


class DraftInvoiceView(BaseFormView):
    """Creates a new draft invoice."""

    form_title = 'Generate new draft invoice'
    form_class = forms.InvoiceForm

    def form_valid(self, form):
        """Bla Bla."""
        db = form.user['db']
        db = muc.draft_time_invoice(db, form.cleaned_data)
        self.request.user.write_data(db)

        return super().form_valid(form)


class DiscardInvoiceView(BaseFormView):
    """
    Uppon confirmation it removes the top invoice from the registry.
    """

    form_title = 'You are about to remove fiscal data. Please confirm.'
    form_class = forms.DiscardInvoiceForm
    template_name = "discard_invoice.html"

    def get_context_data(self, **kwargs):
        """Appends last invoice details to context data"""
        context = super().get_context_data(**kwargs)
        invoices = self.request.user.read_data().invoices()
        context['invoice'] = invoices[0] if invoices else None

        return context

    def form_valid(self, form):
        """User has confirmed, we can trash the last invoice."""
        db = self.request.user.read_data()
        db = muc.discard_last_invoice(db)
        self.request.user.write_data(db)
        return super().form_valid(form)


class TimeInvoiceView(BaseFormView):
    """Allows to mess up with a time invoice."""

    form_title = 'Time Invoice'
    form_class = forms.InvoiceForm
    template_name = 'invoice_detail.html'

    def get_initial(self, **kwargs):
        """Populate invoice using the url argument as index"""
        initial = super().get_initial()
        invoices = self.request.user.read_data().invoices()

        try:
            ndx = int(self.kwargs['invoice_id']) - 1
            invoice = invoices[ndx]
            initial['publish_date'] = invoice.publish_date
            initial['duration'] = invoice.activity.duration
            initial['flavor'] = invoice.activity.flavor
            initial['project_id'] = invoice.activity.project_id
            initial['xchg_rate'] = invoice.conversion_rate
            self.invoice = invoice
        except (IndexError, KeyError):
            raise Http404

        return initial

    def get_context_data(self, **kwargs):
        """Appends last invoice details to context data"""
        context = super().get_context_data(**kwargs)
        if self.invoice:
            context['update_self_url'] = reverse_lazy(
                'microinvoicer_time_invoice', kwargs=self.kwargs)
            context['invoice'] = self.invoice
            context['task_list'] = self.invoice.activity.tasks
            context['invoice_id'] = self.kwargs.get('invoice_id')

        return context


class PrintableInvoiceView(LoginRequiredMixin, View):
    """Download invoice as PDF file"""
        
    def get(self, request, *args, **kwargs):
        """Returns content of generated pdf"""
        db = request.user.read_data()
        try:
            ndx = int(self.kwargs['invoice_id']) - 1
            invoice = db.invoices()[ndx]
        except (IndexError, KeyError):
            raise Http404

        content = muc.render_printable_invoice(invoice)  # content is a BytesIO object 
        response = FileResponse(
            content,
            filename=f'{invoice.series_number}.pdf',
            as_attachment=True,
            content_type='application/pdf'
        )

        return response

class ProfileView(BaseFormView):
    """Captain obvious knows this already."""

    template_name = 'profile.html'
    form_title = 'Your Profile'
    form_class = forms.ProfileForm
