from djongo import models

from django.core.mail import send_mail
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import PermissionManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


from .managers import MicroUserManager
from . import micro_use_cases as muc


class MicroUserData(models.Model):
    data = models.TextField()

    class Meta:
        abstract = True


class MicroUser(AbstractBaseUser, PermissionsMixin):
    """
    For our purposes, it makes much more sense in my opinion to use an email
    address rather than a username

    AbstractBaseUser seems to offer the most flexibility in this regards, as
    we can change the mappings later on
    """
    first_name = models.CharField(_('first name'), max_length=40, blank=False)
    last_name = models.CharField(_('last name'), max_length=40, blank=False)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    datastore = models.TextField(blank=True, default='')
    crc = models.CharField(_('crc32'), max_length=10, blank=False, default='0x0')

    objects = MicroUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('micro user')
        verbose_name_plural = _('micro users')

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def write_data(self, db):
        # TODO: add some validation / exception handling
        self.datastore = muc.dumps(db)
        self.crc = muc.to_crc32(self.datastore)
        self.save()
        print(self.datastore.data)

    def read_data(self):
        # TODO: add some validation / exception handling
        crc = muc.to_crc32(self.datastore)

        if crc != self.crc:
            print('\t >> [warning] crc check failed. did someone messed with your data?')
            print(f'{self.datastore!r}')
            print(f'computed _{crc}_ vs _{self.crc}_ stored')

            self.datastore = ''
            self.crc = muc.to_crc32(self.datastore)
            self.save()

        db = muc.loads(self.datastore)

        return db

