"""Main invoicing application"""
from django.apps import AppConfig
import xml.etree.ElementTree as ET
from .temporary_locale import TemporaryLocale
from datetime import datetime, date
from decimal import Decimal
import locale
import requests


class MicroinvoicerConfig(AppConfig):
    name = "microinvoicer"
    average_rates = dict()
    daily_rates = dict()

    def ready(self) -> None:
        """please note that server must be re-started every day"""

        # load daily rate from bnr
        response = requests.get("https://www.bnr.ro/nbrfxrates.xml")
        response.raise_for_status()
        bnr_daily_tree = ET.fromstring(response.text)
        for it in bnr_daily_tree.iter("{http://www.bnr.ro/xsd}Rate"):
            currency = it.get("currency").lower()
            rate = Decimal(it.text)
            self.daily_rates[currency] = rate

        today = next(bnr_daily_tree.iter("{http://www.bnr.ro/xsd}Cube"))
        print("Parsed BNR daily rate for", today.get("date"))

        # load monthly average from local xml copy
        bnr_average_tree = ET.parse("microinvoicer/bnr-data/bnr-monthly-avg.xml")

        most_recent = date(2005, 1, 1)
        with TemporaryLocale("ro_RO"):
            for it in bnr_average_tree.iter("{http://www.bnr.ro/xsd}Row"):
                _, data, curs = tuple(it.iter())
                month = datetime.strptime(data.text, "%b. %Y").date()
                if month > most_recent:
                    most_recent = month
                rate = Decimal(locale.atof(curs.text))
                # self.average_rates[month] = rate
        print("Loaded BNR rates up to", most_recent.strftime("%Y-%m-%d"), flush=True)
