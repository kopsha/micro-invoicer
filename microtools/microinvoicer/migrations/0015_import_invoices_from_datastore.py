import json
from decimal import Decimal
from django.conf import settings
from django.db import migrations
from django.db.migrations.operations.special import RunPython
from cryptography.fernet import InvalidToken
from django.utils.dateparse import parse_date

from microinvoicer import micro_use_cases as muc


def import_invoices(apps, schema_editor):
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
    FiscalEntity = apps.get_model("microinvoicer", "FiscalEntity")
    ServiceContract = apps.get_model("microinvoicer", "ServiceContract")
    TimeInvoice = apps.get_model("microinvoicer", "TimeInvoice")
    print("")
    for user in MicroUser.objects.all():
        registry = user.registries.first()
        print(f"Account: {user.seller.name}")
        raw_data = read_data(user)
        for raw_invoice in raw_data["register"]["invoices"]:
            buyers = FiscalEntity.objects.filter(fiscal_code=raw_invoice["buyer"]["fiscal_code"])
            if raw_invoice["buyer"]["name"] == "SPYHCE SRL":
                print(" -- exception SPHYCE")
                buyers = FiscalEntity.objects.filter(fiscal_code=raw_invoice["buyer"]["registration_id"])
            assert len(buyers) == 1
            buyer = buyers.first()

            raw_invoice.pop("seller")
            bin_buyer = raw_invoice.pop("buyer")
            activity = raw_invoice.pop("activity")

            # find contract
            if bin_buyer["fiscal_code"] == "qwertyuio":
                print(" -- exception CASH COW")
                raw_invoice["hourly_rate"] = 15
            contracts = ServiceContract.objects.filter(buyer=buyer, unit_rate=Decimal(raw_invoice["hourly_rate"]))

            assert len(contracts) == 1
            contract = contracts.first()
            duration = 0
            for task in activity["tasks"]:
                duration += task["duration"]
            assert duration > 1
            invoice = TimeInvoice(
                registry=registry,
                seller=user.seller,
                buyer=buyer,
                contract=contract,
                series=raw_invoice["series"],
                number=raw_invoice["number"],
                status=raw_invoice["status"],
                issue_date=parse_date(raw_invoice["publish_date"]),
                currency="ron",
                conversion_rate=raw_invoice["conversion_rate"],
                unit="hr",
                unit_rate=raw_invoice["hourly_rate"],
                quantity=duration,
            )

        # user.save()  # just to be sure
    raise RuntimeError("wait")

class Migration(migrations.Migration):

    dependencies = [
        ('microinvoicer', '0014_auto_20210829_1855'),
    ]

    operations = [
        migrations.RunPython(import_invoices, reverse_code=RunPython.noop),
    ]
