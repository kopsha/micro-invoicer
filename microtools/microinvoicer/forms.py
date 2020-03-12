from django.forms import ModelForm
from django_registration.forms import RegistrationForm

from .models import *

class MicroRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = MicroUser
        fields = '__all__'


class FiscalEntityForm(ModelForm):
    class Meta:
        model = FiscalEntity
        fields = '__all__'
