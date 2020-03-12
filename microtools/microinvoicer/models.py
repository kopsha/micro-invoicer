from django.db import models
from django.contrib.auth.models import AbstractUser

class MicroUser(AbstractUser):
    fiscal_code = models.CharField(max_length=16, null=False, blank=True)
