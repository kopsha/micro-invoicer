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
    "no-background": True,
}


def render_timesheet(invoice: TimeInvoice, timesheet):
    country = invoice.buyer.country
    international = True
    if country == "RO":
        locale.setlocale(locale.LC_ALL, "ro_RO")
        international = False
    elif country in {"CH", "IE", "NL"}:
        locale.setlocale(locale.LC_ALL, "en_IE")
    else:
        raise RuntimeError(f"Locale settings not defined for {country}")

    tr_invoice = translate_invoice(invoice, international)
    tr_invoice["seller"] = invoice.seller
    tr_invoice["buyer"] = invoice.buyer
    tr_invoice["tasks"] = timesheet["tasks"]
    options = dict(RENDER_OPTIONS)
    tr_invoice["invoice_title"] = options["title"] = (
        "Annex: Timesheet Report" if international else "Anexa: Raport de Activitate"
    )
    html_content = render_to_string("pdf_timesheet_template.html", context=tr_invoice)
    pdf_content = pdfkit.from_string(html_content, options=options)
    buffer = io.BytesIO(pdf_content)

    return buffer


def render_invoice(invoice: TimeInvoice):
    country = invoice.buyer.country
    international = True
    if country == "RO":
        locale.setlocale(locale.LC_ALL, "ro_RO")
        international = False
    elif country in {"CH", "IE", "NL"}:
        locale.setlocale(locale.LC_ALL, "en_IE")
    else:
        raise RuntimeError(f"Locale settings not defined for {country}")

    tr_invoice = translate_invoice(invoice, international)
    options = dict(RENDER_OPTIONS)
    options["title"] = tr_invoice["invoice_title"]
    html_content = render_to_string("pdf_time_invoice_template.html", context=tr_invoice)
    pdf_content = pdfkit.from_string(html_content, options=options)
    buffer = io.BytesIO(pdf_content)

    return buffer


def translate_invoice(invoice: TimeInvoice, international) -> dict:
    data = dict(
        international=international,
        head=create_header_data(invoice, international),
        invoice_title="INVOICE" if international else "FACTURA",
        invoice_series_number=invoice.series_number,
        invoice_issue_date=invoice.issue_date,
        subtitle_no="no:" if international else "nr:",
        subtitle_from="date:" if international else "din:",
        invoice_description=invoice.description,
        invoice_quantity=invoice.quantity,
        invoice_unit=translate_units(invoice.unit, international),
        invoice_conversion_rate=invoice.conversion_rate,
        invoice_price=locale.currency(
            invoice.unit_rate * (invoice.conversion_rate or 1),
            grouping=True,
            international=international,
        ),
        invoice_vat_perc=f"{invoice.include_vat}%",
        invoice_vat=locale.currency(
            invoice.vat_value(), grouping=True, international=international
        ),
        invoice_time_value=locale.currency(
            invoice.time_value(), grouping=True, international=international
        ),
        invoice_attached_description=invoice.attached_description,
        invoice_attached_cost=locale.currency(
            invoice.attached_cost or 0, grouping=True, international=international
        ),
        invoice_value=locale.currency(invoice.value, grouping=True, international=international),
    )

    return data


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
