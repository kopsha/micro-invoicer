from django.db import models

from django.core.mail import send_mail
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.conf import settings

from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet

from .managers import MicroUserManager
from . import micro_use_cases as muc


SHORT_TEXT = 40
REALLY_SHORT = 16


class MicroUser(AbstractBaseUser, PermissionsMixin):
    """
    For our purposes, it makes much more sense in my opinion to use an email
    address rather than a username

    AbstractBaseUser seems to offer the most flexibility in this regards, as
    we can change the mappings later on
    """
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=SHORT_TEXT)
    last_name = models.CharField(max_length=SHORT_TEXT)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    datastore = models.TextField(blank=True, default="")
    crc = models.CharField(max_length=10, default="0x0")

    objects = MicroUserManager()
    crypto_engine = Fernet(settings.MICRO_USER_SECRET)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def write_data(self, db):
        plain_data = muc.dumps(db)
        self.crc = muc.to_crc32(plain_data)
        self.datastore = MicroUser.crypto_engine.encrypt(plain_data.encode("utf-8")).decode("utf-8")
        self.save()

    def read_data(self):
        try:
            data = self.datastore.encode("utf-8")
            plain_data = str(MicroUser.crypto_engine.decrypt(data), "utf-8")
        except InvalidToken:
            print("\t >> [warning] cannot decrypt invalid user data. raw data dump:")
            print(f"{data!r}")
            empty_db = muc.corrupted_storage()
            plain_data = muc.dumps(empty_db)

        crc = muc.to_crc32(plain_data)
        if crc != self.crc:
            print("\t >> [warning] crc check failed. did someone messed with your data?")
            print(f"\t >> [warning] computed _{crc}_ vs _{self.crc}_ stored.")

        db = muc.loads(plain_data)

        return db

class MicroRegistry(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MicroUser, on_delete=models.CASCADE)

    display_name = models.CharField(max_length=SHORT_TEXT)
    invoice_series = models.CharField(max_length=REALLY_SHORT)
    next_invoice_no = models.IntegerField()
