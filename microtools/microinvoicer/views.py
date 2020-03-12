from django.shortcuts import render
from django.http import HttpResponse

from django_registration.backends.one_step.views import RegistrationView
from . import forms


def index(request):
    return HttpResponse("Hello, bo$$.")


class MicroRegistrationView(RegistrationView):
    form_class = forms.MicroRegistrationForm

    def register(self, form):
        print('registering', form.data)

