from django.db import models

from django.core.mail import send_mail
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import PermissionManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .managers import MicroUserManager

from dataclasses import dataclass, asdict, field
from datetime import datetime, date, timedelta
from typing import List
import enum


class MicroUser(AbstractBaseUser, PermissionsMixin):
    """
    For our purposes, it makes much more sense in my opinion to use an email
    address rather than a username

    AbstractBaseUser seems to offer the most flexibility in this regards, as
    we can change the mappings later on
    """
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MicroUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('micro user')
        verbose_name_plural = _('micro users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


"""
Dataclasses area
"""

@dataclass
class FiscalEntity:
    name: str
    registration_id: str
    fiscal_code: str
    address: str
    bank_account: str
    bank_name: str


@dataclass
class ServiceContract:
    buyer: FiscalEntity
    hourly_rate: float


@dataclass
class Task:
    name: str
    date: date
    duration: float
    project_id: str


@dataclass
class ActivityReport:
    contract_id: int
    start_date: date
    flavor: str
    project_id: str
    tasks: List[Task] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return sum(t.duration for t in self.tasks)


@enum.unique
class InvoiceStatus(enum.IntEnum):
    DRAFT = enum.auto()
    PUBLISHED = enum.auto()
    STORNO = enum.auto()


@dataclass
class TimeInvoice:
    seller: FiscalEntity
    buyer: FiscalEntity
    activity: ActivityReport
    series: str
    number: int
    status: InvoiceStatus
    conversion_rate: float
    hourly_rate: float

    @property
    def series_number(self):
        return f'{self.series}-{self.number:04}'

    @property
    def unit_price(self):
        return self.conversion_rate * self.hourly_rate

    @property
    def value(self):
        return self.unit_price * self.activity.duration

    def __repr__(self):
        return f'{self.series_number:>11} : {self.buyer.name:32} : {self.activity.duration:7.0f} ore : {self.value:11.02f} lei'


@dataclass
class InvoiceRegister:
    seller: FiscalEntity
    invoice_series: str
    next_number: int
    invoices: List[TimeInvoice] = field(default_factory=list)

@dataclass
class LocalStorage:
    register: InvoiceRegister
    contracts: List[ServiceContract] = field(default_factory=list)
