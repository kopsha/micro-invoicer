"""Disabled"""
from django.db import migrations
from django.db.migrations.operations.special import RunPython


class Migration(migrations.Migration):

    dependencies = [
        ('microinvoicer', '0011_auto_20210829_0937'),
    ]

    operations = [
        migrations.RunPython(RunPython.noop, reverse_code=RunPython.noop),
    ]
