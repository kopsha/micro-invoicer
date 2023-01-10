#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
import io
from django.template.loader import render_to_string
import pdfkit

from .models import TimeInvoice


RENDER_OPTIONS = {
    "page-size": "A4",
    "orientation": "Portrait",
    "margin-top": "9mm",
    "margin-right": "9mm",
    "margin-bottom": "9mm",
    "margin-left": "18mm",
    "encoding": "UTF-8",
    "custom-header": [("Accept-Encoding", "gzip")],
}

def render_timesheet(invoice, timesheet):
    return ""


def render_invoice(invoice: TimeInvoice):

    print(invoice.__dict__)


    country = invoice.buyer.country
    international = True
    if country == "RO":
        locale.setlocale(locale.LC_ALL, "ro_RO")
        international = False
    elif country in {"CH", "IE"}:
        locale.setlocale(locale.LC_ALL, "en_IE")
    else:
        raise RuntimeError(f"Locale settings not defined for {country}")

    unit = translate_units(invoice.unit, international)
    context = dict(
        head=create_header_data(invoice, international),
        invoice=invoice,
        invoice_title="INVOICE " if international else "FACTURA " + invoice.series_number,
        subtitle_no="no:" if international else "nr:",
        subtitle_from="date:" if international else "din:",
        invoice_unit=unit,
        invoice_price=locale.currency(
            invoice.unit_rate * (invoice.conversion_rate or 1), grouping=True, international=international
        ),
        invoice_vat=locale.currency(invoice.vat_value(), grouping=True, international=international),
        invoice_time_value=locale.currency(invoice.time_value(), grouping=True, international=international),
        invoice_value=locale.currency(invoice.value, grouping=True, international=international),
    )

    html_content = render_to_string("pdf_time_invoice_template.html", context=context)
    pdf_content = pdfkit.from_string(html_content, options=RENDER_OPTIONS)
    buffer = io.BytesIO(pdf_content)

    return buffer


def translate_units(original, international):
    translation = {"mo": ("luni", "month(s)"), "hr": ("ore", "hour(s)"), "d": ("zile", "day(s)")}
    return translation.get(original, original)[international]


def create_header_data(invoice, international):
    header = dict()
    header["left_first"] = "Supplier:" if international else "Furnizor:"
    header["right_first"] = "Buyer:" if international else "Beneficiar:"
    header["items"] = [
        (invoice.seller.name, invoice.buyer.name),
        (invoice.seller.registration_id, invoice.buyer.registration_id),
        (invoice.seller.fiscal_code, invoice.buyer.fiscal_code),
        (invoice.seller.address, invoice.buyer.address),
        (invoice.seller.country.name, invoice.buyer.country.name),
        (invoice.seller.bank_account, invoice.buyer.bank_account),
        (invoice.seller.bank_name, invoice.buyer.bank_name),
    ]
    return header


if __name__ == "__main__":
    print("This is a pure module, it cannot be executed.")
