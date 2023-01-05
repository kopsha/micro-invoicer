"""How about now."""
from datetime import date
from django.http import FileResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms.models import model_to_dict
from django.template import Template, Context
from django_registration.backends.one_step.views import RegistrationView

from . import forms, models, pdf_rendering, micro_timesheet


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
            user = self.request.user
            context["registries"] = user.registries.prefetch_related(
                "seller", "contracts", "invoices"
            ).all()

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
    model = models.MicroUser
    template_name = "profile.html"
    form_title = "Your Profile"
    fields = ["first_name", "last_name"]

    def get_object(self):
        return self.request.user


class ProfileSetupView(ProfileUpdateView):
    model = models.MicroUser
    form_title = "Setup fiscal information"
    fields = ["email", "first_name", "last_name"]


class RegistryCreateView(MicroFormMixin, CreateView):
    model = models.MicroRegistry
    form_title = "Define new registry"
    form_class = forms.RegistryForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        most_fields = [field.name for field in models.FiscalEntity._meta.get_fields() if field.name != "id"]
        seller_data = {field: form.cleaned_data[field] for field in most_fields}
        seller = models.FiscalEntity(**seller_data)
        seller.save()
        form.instance.seller = seller
        return super().form_valid(form)


class RegistryUpdateView(MicroFormMixin, UpdateView):
    model = models.MicroRegistry
    form_title = "Update registry"
    form_class = forms.RegistryForm

    def form_valid(self, form):
        # update seller information too
        seller = form.instance.seller
        seller_fields = [field.name for field in models.FiscalEntity._meta.get_fields() if field.name != "id"]
        for field in seller_fields:
            setattr(seller, field, form.cleaned_data[field])
        seller.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if seller_instance := self.object.seller:
            seller_data = model_to_dict(
                seller_instance,
                fields=[
                    "name",
                    "owner_fullname",
                    "registration_id",
                    "fiscal_code",
                    "address",
                    "country",
                    "bank_account",
                    "bank_name",
                ],
            )
            initial.update(seller_data)
        return initial


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
            buyer_data = model_to_dict(
                buyer_instance,
                fields=[
                    "name",
                    "owner_fullname",
                    "registration_id",
                    "fiscal_code",
                    "address",
                    "country",
                    "bank_account",
                    "bank_name",
                ],
            )
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
        today = date.today()
        initial["issue_date"] = today
        registry = models.MicroRegistry.objects.get(pk=self.kwargs["registry_id"])
        self.kwargs["registry"] = registry
        last_invoice = registry.invoices.last()
        if last_invoice:
            initial["contract"] = last_invoice.contract
            initial["quantity"] = last_invoice.quantity

            description_template = Template(last_invoice.contract.invoicing_description)
            last_month = today.replace(day=1, month=((today.month + 11) % 12))
            local_context = Context(dict(today=today, last_month=last_month))
            initial["override_description"] = description_template.render(local_context)

        return initial

    def form_valid(self, form):
        """Fill in the missing fields"""
        registry = self.kwargs["registry"]
        contract = form.instance.contract

        form.instance.registry = registry
        form.instance.seller = registry.seller
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

        if form.cleaned_data["attached_cost"] and form.cleaned_data["attached_description"]:
            form.instance.attached_description = form.cleaned_data["attached_description"]
            form.instance.attached_cost = form.cleaned_data["attached_cost"]

        response = super().form_valid(form)
        registry.next_invoice_no += 1
        registry.save()
        return response


class TimeInvoiceDeleteView(MicroFormMixin, DeleteView):
    model = models.TimeInvoice
    form_title = "Throwing away invoice"
    template_name = "confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        invoice = self.get_object()
        invoice.registry.next_invoice_no -= 1
        invoice.registry.save()
        return super().delete(request, *args, **kwargs)


class TimeInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = models.TimeInvoice
    template_name = "invoice_detail.html"


class TimeInvoicePrintView(LoginRequiredMixin, DetailView):
    """Download invoice as PDF file"""

    model = models.TimeInvoice
    response_class = FileResponse

    def render_to_response(self, context, **response_kwargs):
        """Returns content of generated pdf"""
        invoice = context["object"]
        content = pdf_rendering.render_invoice(invoice)
        response = FileResponse(
            content,
            filename=f"{invoice.series_number}.pdf",
            as_attachment=True,
            content_type="application/pdf",
        )
        return response


class TimeInvoiceFakeTimesheetView(LoginRequiredMixin, DetailView):
    """Generate fake timesheet as PDF file"""

    model = models.TimeInvoice
    response_class = FileResponse

    def render_to_response(self, context, **response_kwargs):
        """Returns content of generated pdf"""
        invoice = context["object"]
        timesheet = micro_timesheet.fake_timesheet(invoice.quantity, "Meditatii", "Catalog Online")
        content = pdf_rendering.render_timesheet(invoice, timesheet)
        response = FileResponse(
            content,
            filename=f"{invoice.series_number}-timesheet.pdf",
            as_attachment=True,
            content_type="application/pdf",
        )
        return response
