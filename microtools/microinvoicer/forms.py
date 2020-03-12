from django_registration.forms import RegistrationForm

from . import models

class MicroRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = models.MicroUser
        exclude = []
