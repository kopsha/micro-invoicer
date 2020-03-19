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


class SellerForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    registration_id = forms.CharField(max_length=20, required=True)
    fiscal_code = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=240, required=True)
    bank_account = forms.CharField(max_length=32, required=True)
    bank_name = forms.CharField(max_length=80, required=True)
    invoice_series = forms.CharField(max_length=5, required=True)
    start_no = forms.IntegerField(required=True)
