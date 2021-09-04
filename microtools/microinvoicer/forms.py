from django import forms
from django_registration.forms import RegistrationForm
from django_countries.fields import CountryField
from material import Layout, Row
from . import models


class MicroRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = models.MicroUser
        fields = ["email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    layout = Layout(Row("email"), Row("first_name", "last_name"), Row("password1", "password2"))


class EditablesMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in self.editables:
                self.fields[field].disabled = True


class FiscalEntityForm(forms.ModelForm):
    name = forms.CharField(max_length=models.LONG_TEXT, label="Company name")
    owner_fullname = forms.CharField(max_length=models.LONG_TEXT)
    registration_id = forms.CharField(max_length=models.SHORT_TEXT)
    fiscal_code = forms.CharField(max_length=models.SHORT_TEXT)
    address = forms.CharField(widget=forms.Textarea)
    country = CountryField().formfield()
    bank_account = forms.CharField(max_length=models.SHORT_TEXT)
    bank_name = forms.CharField(max_length=models.LONG_TEXT)


class ProfileUpdateForm(EditablesMixin, FiscalEntityForm):
    class Meta:
        model = models.MicroUser
        fields = ["email", "first_name", "last_name"]

    editables = {"address", "country", "bank_account", "bank_name"}


class ProfileSetupForm(ProfileUpdateForm):
    editables = {
        "email",
        "first_name",
        "last_name",
        "name",
        "owner_fullname",
        "registration_id",
        "fiscal_code",
        "address",
        "country",
        "bank_name",
        "bank_account",
    }


class ServiceContractForm(FiscalEntityForm):
    class Meta:
        model = models.ServiceContract
        fields = [
            "registration_no",
            "registration_date",
            "unit_rate",
            "currency",
            "unit",
            "invoicing_currency",
            "invoicing_description",
        ]

    def __init__(self, *args, **kwargs):
        """reorder fields to get buyer details on top"""
        super().__init__(*args, **kwargs)
        buyer_fields = {key: value for key, value in self.fields.items() if key not in self.Meta.fields}
        self_fields = {key: value for key, value in self.fields.items() if key in self.Meta.fields}
        self.fields = dict(**buyer_fields, **self_fields)


class TimeInvoiceForm(forms.ModelForm):
    class Meta:
        model = models.TimeInvoice
        fields = ["contract", "issue_date", "quantity", "conversion_rate"]

    override_description = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        registry = kwargs.pop("registry")
        super().__init__(*args, **kwargs)
        self.fields["contract"].queryset = models.ServiceContract.objects.filter(registry=registry)
