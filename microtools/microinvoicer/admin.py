from django.contrib import admin

from . import models

admin.site.register(models.MicroUser)
admin.site.register(models.MicroRegistry)
admin.site.register(models.ServiceContract)
admin.site.register(models.FiscalEntity)
