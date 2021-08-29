"""How about now."""
from datetime import date
from django.apps import registry
from django.http import Http404, FileResponse
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms.models import model_to_dict

from django_registration.backends.one_step.views import RegistrationView

from . import forms, models
from . import micro_use_cases as muc


class IndexView(TemplateView):
    """Landing Page."""
    template_name = "index.html"


class MicroRegistrationView(RegistrationView):
    """User registration."""
    template_name = "registration_form.html"
    form_class = forms.MicroRegistrationForm
    # For now, we redirect straight to fiscal information view after signup.
    # When we'll change to two step registration, fiscal form will be shown at
    # the first login
    success_url = reverse_lazy("setup")


class MicroLoginView(LoginView):
    """Classic login."""
    template_name = "login.html"


class MicroHomeView(LoginRequiredMixin, TemplateView):
    """User Home."""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        """Attach all registry info."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["registries"] = self.request.user.registries.prefetch_related("contracts").all()

            db = self.request.user.read_data()
            context["seller"] = {"name": db.register.seller.name}
            context["contracts"] = db.flatten_contracts()
            context["invoices"] = db.invoices()

        return context


class MicroFormMixin(LoginRequiredMixin):
    """Common requirements for model views"""

    template_name = "base_form.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        """Add form title."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = self.form_title
        return context


class ProfileUpdateView(MicroFormMixin, UpdateView):
    """Updates only some seller fields"""

    model = models.MicroUser
    form_class = forms.ProfileUpdateForm
    template_name = "profile.html"
    form_title = "Your Profile"

    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        if seller_instance := self.request.user.seller:
            seller = model_to_dict(seller_instance, fields=[
                "name", "owner_fullname", "registration_id", "fiscal_code",
                "address", "bank_account", "bank_name"
            ])
            initial.update(seller)
        return initial

    def form_valid(self, form):
        """Update only seller info"""
        seller = self.object.seller
        seller.address = form.cleaned_data["address"]
        seller.bank_account = form.cleaned_data["bank_account"]
        seller.bank_name = form.cleaned_data["bank_name"]
        seller.save()
        return super().form_valid(form)


class ProfileSetupView(ProfileUpdateView):
    """
    Updates all user's fiscal information.
    """
    form_class = forms.ProfileSetupForm
    form_title = "Setup fiscal information"

    def form_valid(self, form):
        seller_data = {
            field: form.cleaned_data[field]
            for field in models.FiscalEntity._meta.get_fields()
        }
        seller = models.FiscalEntity(seller_data)
        seller.save()
        self.object.seller = seller
        return super().form_valid(form)


class RegistryCreateView(MicroFormMixin, CreateView):
    model = models.MicroRegistry
    form_title = "Define new registry"
    fields = ["display_name", "invoice_series", "next_invoice_no"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class RegistryUpdateView(MicroFormMixin, UpdateView):
    model = models.MicroRegistry
    form_title = "Update registry"
    fields = ["display_name", "invoice_series", "next_invoice_no"]


class RegistryDeleteView(MicroFormMixin, DeleteView):
    model = models.MicroRegistry
    form_title = "Throwing away whole registry"
    template_name = "confirm_delete.html"


class ContractCreateView(MicroFormMixin, CreateView):
    model = models.ServiceContract
    form_title = "Register new contract"
    form_class = forms.ServiceContractForm

    def form_valid(self, form):
        """Create buyer instance before saving contract"""
        buyer_data = {
            field: form.cleaned_data[field]
            for field in form.cleaned_data
            if field in forms.FiscalEntityForm.declared_fields.keys()
        }
        buyer = models.FiscalEntity(**buyer_data)
        buyer.save()

        form.instance.buyer = buyer
        form.instance.registry = models.MicroRegistry.objects.get(pk=self.kwargs["registry_id"])

        return super().form_valid(form)


class ContractUpdateView(MicroFormMixin, UpdateView):
    model = models.ServiceContract
    form_title = "Modify contract"
    form_class = forms.ServiceContractForm

    def get_initial(self):
        initial = super().get_initial()
        if buyer_instance := self.object.buyer:
            buyer_data = model_to_dict(buyer_instance, fields=[
                "name", "owner_fullname", "registration_id", "fiscal_code",
                "address", "bank_account", "bank_name"
            ])
            initial.update(buyer_data)
        return initial

    def form_valid(self, form):
        """Update buyer instance before saving contract"""
        buyer_data = {
            field: form.cleaned_data[field]
            for field in form.cleaned_data
            if field in forms.FiscalEntityForm.declared_fields.keys()
        }
        form.instance.buyer.__dict__.update(**buyer_data)
        form.instance.buyer.save()

        return super().form_valid(form)


class ContractDeleteView(MicroFormMixin, DeleteView):
    model = models.ServiceContract
    form_title = "Throwing away contract"
    template_name = "confirm_delete.html"


class TimeInvoiceCreateView(MicroFormMixin, CreateView):
    model = models.TimeInvoice
    form_title = "Issue new time invoice"
    form_class = forms.TimeInvoiceForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["registry"] = self.kwargs["registry"]
        return kwargs

    def get_initial(self, **kwargs):
        """provide sensible defaults for a new invoice"""
        initial = super().get_initial()
        initial["issue_date"] = date.today
        registry = models.MicroRegistry.objects.get(pk=self.kwargs["registry_id"])
        self.kwargs["registry"] = registry
        last_invoice = registry.invoices.last()
        if last_invoice:
            initial["contract"] = last_invoice.contract
            initial["quantity"] = last_invoice.quantity

        return initial

    def form_valid(self, form):
        """Fill in the missing fields"""
        registry = self.kwargs["registry"]
        contract = form.instance.contract

        form.instance.registry = registry
        form.instance.seller = registry.user.seller
        form.instance.buyer = contract.buyer
        form.instance.series = registry.invoice_series
        form.instance.number = registry.next_invoice_no
        form.instance.status = models.InvoiceStatus.PUBLISHED
        form.instance.currency = contract.invoicing_currency
        form.instance.unit = contract.unit
        form.instance.unit_rate = contract.unit_rate

        if form.cleaned_data["override_description"]:
            form.instance.description = form.cleaned_data["override_description"]
        else:
            form.instance.description = contract.invoicing_description

        response = super().form_valid(form)
        registry.next_invoice_no += 1
        registry.save()
        return response


###############################################

class BaseFormView(LoginRequiredMixin, FormView):
    """Extend this view for any form."""

    template_name = "base_form.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        """Add form title."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = self.form_title

        return context

    def get_form_kwargs(self):
        """Adds user information required for later validation."""
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class DraftInvoiceView(BaseFormView):
    """Creates a new draft invoice."""

    form_title = "Create a new invoice"
    form_class = forms.InvoiceForm

    def get_initial(self, **kwargs):
        """provide sensible defaults for a new invoice"""
        initial = super().get_initial()
        db = self.request.user.read_data()

        all_invoices = db.invoices()
        if all_invoices:
            last_invoice = all_invoices[0]
            initial["duration"] = last_invoice.activity.duration
            initial["flavor"] = last_invoice.activity.flavor
            initial["project_id"] = last_invoice.activity.project_id

        return initial

    def form_valid(self, form):
        """Bla Bla."""
        db = form.user["db"]
        db = muc.draft_time_invoice(db, form.cleaned_data)
        self.request.user.write_data(db)

        return super().form_valid(form)


class DiscardInvoiceView(BaseFormView):
    """
    Uppon confirmation it removes the top invoice from the registry.
    """

    form_title = "You are about to remove fiscal data. Please confirm."
    form_class = forms.DiscardInvoiceForm
    template_name = "discard_invoice.html"

    def get_context_data(self, **kwargs):
        """Appends last invoice details to context data"""
        context = super().get_context_data(**kwargs)
        invoices = self.request.user.read_data().invoices()
        context["invoice"] = invoices[0] if invoices else None

        return context

    def form_valid(self, form):
        """User has confirmed, we can trash the last invoice."""
        db = self.request.user.read_data()
        db = muc.discard_last_invoice(db)
        self.request.user.write_data(db)
        return super().form_valid(form)


class TimeInvoiceView(BaseFormView):
    """Allows to mess up with a time invoice."""

    form_title = "Time Invoice"
    form_class = forms.InvoiceForm
    template_name = "invoice_detail.html"

    def get_initial(self, **kwargs):
        """Populate invoice using the url argument as index"""
        initial = super().get_initial()
        invoices = self.request.user.read_data().invoices()

        try:
            ndx = int(self.kwargs["invoice_id"]) - 1
            invoice = invoices[ndx]
            initial["publish_date"] = invoice.publish_date
            initial["duration"] = invoice.activity.duration
            initial["flavor"] = invoice.activity.flavor
            initial["project_id"] = invoice.activity.project_id
            initial["xchg_rate"] = invoice.conversion_rate
            self.invoice = invoice
        except (IndexError, KeyError):
            raise Http404

        return initial

    def get_context_data(self, **kwargs):
        """Appends last invoice details to context data"""
        context = super().get_context_data(**kwargs)
        if self.invoice:
            context["update_self_url"] = reverse_lazy("microinvoicer_time_invoice", kwargs=self.kwargs)
            context["invoice"] = self.invoice
            context["task_list"] = self.invoice.activity.tasks
            context["invoice_id"] = self.kwargs.get("invoice_id")

        return context


class PrintableInvoiceView(LoginRequiredMixin, View):
    """Download invoice as PDF file"""

    def get(self, request, *args, **kwargs):
        """Returns content of generated pdf"""
        db = request.user.read_data()
        try:
            ndx = int(self.kwargs["invoice_id"]) - 1
            invoice = db.invoices()[ndx]
        except (IndexError, KeyError):
            raise Http404

        content = muc.render_printable_invoice(invoice)  # content is a BytesIO object
        response = FileResponse(
            content,
            filename=f"{invoice.series_number}.pdf",
            as_attachment=True,
            content_type="application/pdf",
        )

        return response
