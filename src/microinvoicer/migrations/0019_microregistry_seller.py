# Generated by Django 3.2.7 on 2021-09-04 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('microinvoicer', '0018_auto_20210904_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='microregistry',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='microinvoicer.fiscalentity'),
        ),
    ]
