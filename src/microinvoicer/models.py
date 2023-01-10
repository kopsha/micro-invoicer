from django.db import models
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django_countries.fields import CountryField

from .managers import MicroUserManager


LONG_TEXT = 255
SHORT_TEXT = 40
REALLY_SHORT = 16


class AvailableCurrencies(models.TextChoices):
    EUR = "eur", "Euros"
    USD = "usd", "US Dollars"
    RON = "ron", "Lei"


class InvoicingUnits(models.TextChoices):
    MONTHLY = "mo", "Month"
    DAILY = "d", "Day"
    HOURLY = "hr", "Hour"


class InvoiceStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    PUBLISHED = 1, "Published"
    STORNO = 2, "Storno"


class FiscalEntity(models.Model):
    name = models.CharField(max_length=LONG_TEXT)
    owner_fullname = models.CharField(max_length=LONG_TEXT)
    registration_id = models.CharField(max_length=SHORT_TEXT)
    fiscal_code = models.CharField(max_length=SHORT_TEXT)
    address = models.TextField()
    country = CountryField(default="RO")
    bank_account = models.CharField(max_length=SHORT_TEXT)
    bank_name = models.CharField(max_length=LONG_TEXT)

    def __repr__(self) -> str:
        return f"{self.name}"

    def __str__(self):
        return repr(self)


class MicroUser(AbstractBaseUser, PermissionsMixin):
    """User account, which holds the service provider (seller) entity"""

    first_name = models.CharField(max_length=SHORT_TEXT)
    last_name = models.CharField(max_length=SHORT_TEXT)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = MicroUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class MicroRegistry(models.Model):
    user = models.ForeignKey(MicroUser, related_name="registries", on_delete=models.CASCADE)
    seller = models.ForeignKey(FiscalEntity, related_name="+", on_delete=models.CASCADE)

    display_name = models.CharField(max_length=SHORT_TEXT)
    invoice_series = models.CharField(max_length=REALLY_SHORT)
    next_invoice_no = models.IntegerField()
    include_vat = models.IntegerField(
        verbose_name="Apply VAT (%)",
        default=0,
        validators=(
            MinValueValidator(0),
            MaxValueValidator(100),
        ),
    )

    def __repr__(self) -> str:
        return f"{self.display_name}, series {self.invoice_series}, {self.contracts.count()} contracts and ..."

    def __str__(self):
        return repr(self)


class ServiceContract(models.Model):
    buyer = models.ForeignKey(FiscalEntity, related_name="+", on_delete=models.RESTRICT)
    registry = models.ForeignKey(MicroRegistry, related_name="contracts", on_delete=models.CASCADE)

    registration_no = models.CharField("Contract number", max_length=SHORT_TEXT)
    registration_date = models.DateField("Contract date")
    currency = models.CharField(max_length=3, choices=AvailableCurrencies.choices)
    unit = models.CharField(max_length=2, choices=InvoicingUnits.choices)
    unit_rate = models.DecimalField(max_digits=16, decimal_places=2)
    invoicing_currency = models.CharField(max_length=3, choices=AvailableCurrencies.choices)
    invoicing_description = models.CharField(
        "Service description template", max_length=LONG_TEXT, blank=True
    )

    def __repr__(self) -> str:
        return f"{self.buyer!r}, {self.unit_rate} {self.currency}/{self.unit}"

    def __str__(self):
        return repr(self)


class TimeInvoice(models.Model):
    registry = models.ForeignKey(MicroRegistry, related_name="invoices", on_delete=models.CASCADE)
    seller = models.ForeignKey(FiscalEntity, related_name="+", on_delete=models.RESTRICT)
    buyer = models.ForeignKey(FiscalEntity, related_name="+", on_delete=models.RESTRICT)
    contract = models.ForeignKey(ServiceContract, related_name="+", on_delete=models.RESTRICT)

    series = models.CharField(max_length=REALLY_SHORT)
    number = models.IntegerField()
    status = models.IntegerField(choices=InvoiceStatus.choices)
    description = models.CharField(max_length=LONG_TEXT, blank=True)
    currency = models.CharField(max_length=3, choices=AvailableCurrencies.choices)
    conversion_rate = models.DecimalField(
        max_digits=16, decimal_places=4, null=True
    )  # contract currency to invoice currency
    unit = models.CharField(max_length=2, choices=InvoicingUnits.choices)
    unit_rate = models.DecimalField(max_digits=16, decimal_places=2)

    attached_cost = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    attached_description = models.CharField(max_length=LONG_TEXT, blank=True, null=True)

    issue_date = models.DateField()
    quantity = models.IntegerField()
    include_vat = models.IntegerField(default=0)

    @property
    def series_number(self):
        return f"{self.series}-{self.number:04}"

    @property
    def value(self):
        return self.time_value() + self.vat_value() + (self.attached_cost or 0)

    def time_value(self):
        conversion = self.conversion_rate or 1
        return self.unit_rate * self.quantity * conversion

    def vat_value(self):
        return (self.time_value() * self.include_vat) / 100

    @property
    def contract_currency(self):
        return self.contract.currency

    def __repr__(self) -> str:
        return f"{self.series_number} for {self.buyer}"

    def __str__(self):
        return repr(self)
