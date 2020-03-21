from django import forms
from django_registration.forms import RegistrationForm

from material import Layout, Row

from .models import MicroUser


class MicroRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = MicroUser
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    layout = Layout(
        Row('email'),
        Row('first_name', 'last_name'),
        Row('password1', 'password2')
    )


class FiscalEntityForm(forms.Form):
    name = forms.CharField(max_length=120, required=True, strip=True)
    owner_fullname = forms.CharField(max_length=80, required=True, strip=True)
    registration_id = forms.CharField(max_length=20, required=True, strip=True)
    fiscal_code = forms.CharField(max_length=15, required=True, strip=True)
    address = forms.CharField(max_length=240, required=True, strip=True)
    bank_account = forms.CharField(max_length=32, required=True, strip=True)
    bank_name = forms.CharField(max_length=80, required=True, strip=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        super().__init__(*args, **kwargs)


class SellerForm(FiscalEntityForm):
    invoice_series = forms.CharField(max_length=5, required=True)
    start_no = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner_fullname'].initial = self.user.get_full_name()


class BuyerForm(FiscalEntityForm):
    hourly_rate = forms.DecimalField(required=True, decimal_places=2)
