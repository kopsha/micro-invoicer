# Generated by Django 3.0.4 on 2020-03-19 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microinvoicer', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FiscalEntity',
        ),
        migrations.AddField(
            model_name='microuser',
            name='datastore',
            field=models.TextField(blank=True),
        ),
    ]
