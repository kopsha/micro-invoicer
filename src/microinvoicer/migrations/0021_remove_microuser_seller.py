# Generated by Django 3.2.7 on 2021-09-04 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('microinvoicer', '0020_copy_seller'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='microuser',
            name='seller',
        ),
    ]
