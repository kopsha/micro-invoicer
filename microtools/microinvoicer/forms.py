from dataclasses import asdict
from django import forms
from django_registration.forms import RegistrationForm
from material import Layout, Row
from django.forms.models import model_to_dict

from datetime import date

from .models import MicroUser


class MicroRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = MicroUser
        fields = ["email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    layout = Layout(Row("email"), Row("first_name", "last_name"), Row("password1", "password2"))


class BaseUserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        self.user = {
            "full_name": user.get_full_name(),
            "email": user.email,
            "db": user.read_data(),
        }
        super().__init__(*args, **kwargs)


class FiscalEntityForm(BaseUserForm):
    name = forms.CharField(max_length=80, required=True, strip=True, label="Company name")
    owner_fullname = forms.CharField(max_length=80, required=True, strip=True)
    registration_id = forms.CharField(max_length=20, required=True, strip=True)
    fiscal_code = forms.CharField(max_length=15, required=True, strip=True)
    address = forms.CharField(max_length=240, required=True, strip=True)
    bank_account = forms.CharField(max_length=32, required=True, strip=True)
    bank_name = forms.CharField(max_length=80, required=True, strip=True)


class ProfileForm(FiscalEntityForm):
    full_name = forms.CharField(max_length=80, disabled=True)
    email = forms.EmailField(disabled=True)

    field_order = [
        "email",
        "full_name",
        "date_joined",
        "name",
        "owner_fullname",
        "registration_id",
        "fiscal_code",
        "address",
        "bank_name",
        "bank_account",
    ]
    fields = field_order

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # user fields
        self.fields["full_name"].initial = self.user["full_name"]
        self.fields["email"].initial = self.user["email"]

        # company fields
        if self.user["db"]:
            for f, value in asdict(self.user["db"].register.seller).items():
                self.fields[f].initial = value

        # ATTENTION: please match this with use cases, sometime
        editables = [
            "address",
            "bank_name",
            "bank_account",
        ]
        for f in self.base_fields:
            self.fields[f].disabled = True if f not in editables else False


class SellerForm(FiscalEntityForm):
    invoice_series = forms.CharField(max_length=5, required=True)
    start_no = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db = self.user["db"]
        if db.register.seller.registration_id not in {"(corrupted)"}:
            for f, value in asdict(db.register.seller).items():
                self.fields[f].initial = value
            self.fields["invoice_series"].initial = db.register.invoice_series
            self.fields["start_no"].initial = db.register.next_number

        if not self.fields["owner_fullname"].initial:
            self.fields["owner_fullname"].initial = self.user["full_name"]


class ContractForm(FiscalEntityForm):
    registry_id = forms.CharField(required=True, max_length=8, strip=True, label="Registry number")
    registry_date = forms.DateField(required=True, label="Registry date")
    hourly_rate = forms.DecimalField(required=True, decimal_places=2)


class InvoiceForm(BaseUserForm):
    publish_date = forms.DateField(required=True, initial=date.today, label="Invoice date")
    contract_id = forms.ChoiceField(required=True, label="Choose contract")
    duration = forms.IntegerField(required=True, min_value=1, label_suffix="hours")
    flavor = forms.CharField(required=True, max_length=80, strip=True)
    project_id = forms.CharField(required=True, max_length=80, strip=True)
    xchg_rate = forms.DecimalField(
        label="Exchange rate",
        label_suffix="lei / euro",
        decimal_places=4,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contract_id"].choices = (
            (i, f"{c.buyer.name}, {c.hourly_rate} euro / hour")
            for i, c in enumerate(self.user["db"].contracts)
        )


class DiscardInvoiceForm(BaseUserForm):
    confirmed = forms.BooleanField(required=True, label="Do it!", initial=False)
