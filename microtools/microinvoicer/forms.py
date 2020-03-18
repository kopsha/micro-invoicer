from django.forms import ModelForm
from django_registration.forms import RegistrationForm

from material import Layout, Row

from .models import MicroUser, FiscalEntity


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


class FiscalEntityForm(ModelForm):
    class Meta:
        model = FiscalEntity
        fields = '__all__'
