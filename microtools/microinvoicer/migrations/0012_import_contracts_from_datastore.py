import json
from django.apps import registry

from django.conf import settings
from django.db import migrations
from django.db.migrations.operations.special import RunPython
from cryptography.fernet import InvalidToken
from django.utils.dateparse import parse_date

from microinvoicer import micro_use_cases as muc


def import_registry_contracts(apps, schema_editor):
    def read_data(user):
        try:
            encrypted_data = user.datastore.encode("utf-8")
            plain_data = str(settings.CRYPTO_ENGINE.decrypt(encrypted_data), "utf-8")
        except InvalidToken:
            print("\t >> [warning] cannot decrypt invalid user data. raw data dump:")
            print(f"{encrypted_data!r}")
            plain_data = ""

        crc = muc.to_crc32(plain_data)
        if crc != user.crc:
            print("\t >> [warning] crc check failed. did someone messed with your data?")
            print(f"\t >> [warning] computed _{crc}_ vs _{user.crc}_ stored.")

        return json.loads(plain_data)

    MicroUser = apps.get_model("microinvoicer", "MicroUser")
    MicroRegistry = apps.get_model("microinvoicer", "MicroRegistry")
    FiscalEntity = apps.get_model("microinvoicer", "FiscalEntity")
    ServiceContract = apps.get_model("microinvoicer", "ServiceContract")
    for user in MicroUser.objects.all():
        raw_data = read_data(user)

        # import registry
        reg = MicroRegistry(
            display_name="Servicii interne",
            invoice_series=raw_data["register"]["invoice_series"],
            next_invoice_no=raw_data["register"]["next_number"],
            user=user,
        )
        reg.save()

        # import contracts
        for raw_contract in raw_data["contracts"]:
            buyer = FiscalEntity(**raw_contract["buyer"])
            buyer.save()
            contract = ServiceContract(
                buyer=buyer,
                registration_no=raw_contract["registry_id"],
                registration_date=parse_date(raw_contract["registry_date"]),
                unit_rate=raw_contract["hourly_rate"],
                unit="hr",
                currency="eur",
                invoice_currency="ron",
                registry=reg
            )
            contract.save()

        user.save()  # just to be sure


class Migration(migrations.Migration):

    dependencies = [
        ('microinvoicer', '0011_auto_20210829_0937'),
    ]

    operations = [
        migrations.RunPython(import_registry_contracts, reverse_code=RunPython.noop),
    ]
