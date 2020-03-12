from django.db import models
from django.contrib.auth.models import AbstractUser

class MicroUser(AbstractUser):
    fiscal_code = models.CharField(max_length=16, null=False, blank=True)


class FiscalEntity(models.Model):
    name: models.CharField(null=False, blank=False)
    registration_id: models.CharField(null=False, blank=False)
    fiscal_code: models.CharField(null=False, blank=False)
    address: models.CharField(null=False, blank=False)
    bank_account: models.CharField(null=False, blank=False)
    bank_name: models.CharField(null=False, blank=False)
