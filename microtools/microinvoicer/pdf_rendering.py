#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO


pdfmetrics.registerFont(TTFont("Helvetica Neue", "HelveticaNeue.ttc"))
# some local settings, keep lowercase
page_width, page_height = (21.0, 29.7)
row_height = 0.5
row_space = 0.1
top_margin = page_height - 1.1
bottom_margin = 0.7
left_margin = 1.9
right_margin = page_width - 1.1

font_tiny = 8
font_small = 10
font_normal = 11
font_subtitle = 14
font_title = 20


def render_timesheet(invoice, timesheet):
    write_buffer = BytesIO()
    pdf = canvas.Canvas(filename=write_buffer, pagesize=A4)
    pdf.setAuthor("{} [{}]".format(invoice.seller.owner_fullname, invoice.seller.name))
    pdf.setTitle(f"Timesheet for {invoice.series_number}")
    pdf.setSubject(
        "acc. contract {} / {}".format(
            invoice.contract.registration_no, invoice.contract.registration_date.strftime("%d-%b-%Y")
        )
    )
    pdf.setCreator("microtools@fibonet.ro")

    country = invoice.buyer.country
    if country == "RO":
        locale.setlocale(locale.LC_ALL, "ro_RO")
        render_timesheet_ro(pdf, invoice, timesheet)
    elif country == "CH":
        locale.setlocale(locale.LC_ALL, "en_IE")
        render_timesheet_en(pdf, invoice, timesheet)
    else:
        raise RuntimeError(f"Locale settings not defined for {country}")

    pdf.save()
    write_buffer.seek(0)

    return write_buffer


def render_invoice(invoice):
    write_buffer = BytesIO()
    pdf = canvas.Canvas(filename=write_buffer, pagesize=A4)
    pdf.setAuthor("{} [{}]".format(invoice.seller.owner_fullname, invoice.seller.name))
    pdf.setTitle(f"Invoice {invoice.series_number}")
    pdf.setSubject(
        "acc. contract {} / {}".format(
            invoice.contract.registration_no, invoice.contract.registration_date.strftime("%d-%b-%Y")
        )
    )
    pdf.setCreator("microtools@fibonet.ro")

    country = invoice.buyer.country
    if country == "RO":
        locale.setlocale(locale.LC_ALL, "ro_RO")
        render_invoice_ro(pdf, invoice)
    elif country == "CH":
        locale.setlocale(locale.LC_ALL, "en_IE")
        render_invoice_en(pdf, invoice)
    else:
        raise RuntimeError(f"Locale settings not defined for {country}")

    pdf.save()
    write_buffer.seek(0)

    return write_buffer


def render_invoice_ro(pdf, invoice):
    title = f"FACTURA"

    header = create_ro_header_data(invoice)
    render_header(pdf, header)
    bottom = render_title(pdf, title)
    bottom = render_invoice_subtitle(pdf, invoice, from_y=bottom)
    bottom = render_invoice_items(pdf, invoice, from_y=bottom)

    render_watermark(pdf)
    pdf.showPage()


def render_invoice_en(pdf, invoice):
    title = f"INVOICE"

    header = create_en_header_data(invoice)
    render_header(pdf, header)
    bottom = render_title(pdf, title)
    bottom = render_invoice_subtitle(pdf, invoice, from_y=bottom, international=True)
    bottom = render_invoice_items(pdf, invoice, from_y=bottom, international=True)

    render_watermark(pdf)
    pdf.showPage()


def to_cm(xu, yu):
    return (xu * cm, yu * cm)


def translate_units(original, international):
    translation = {"mo": ("luni", "month(s)"), "hr": ("ore", "hour(s)")}
    return translation.get(original, original)[international]


def create_ro_header_data(invoice):
    header = dict()
    header["left"] = [
        "Furnizor:",
        invoice.seller.name,
        invoice.seller.registration_id,
        invoice.seller.fiscal_code,
        invoice.seller.address,
        invoice.seller.bank_account,
        invoice.seller.bank_name,
    ]
    header["right"] = [
        "Beneficiar:",
        invoice.buyer.name,
        invoice.buyer.registration_id,
        invoice.buyer.fiscal_code,
        invoice.buyer.address,
        invoice.buyer.bank_account,
        invoice.buyer.bank_name,
    ]
    return header


def create_en_header_data(invoice):
    header = dict()
    header["left"] = [
        "Supplier:",
        invoice.seller.name,
        invoice.seller.registration_id,
        invoice.seller.fiscal_code,
        invoice.seller.address,
        invoice.seller.country.name,
        invoice.seller.bank_account,
        invoice.seller.bank_name,
    ]
    header["right"] = [
        "Buyer:",
        invoice.buyer.name,
        invoice.buyer.registration_id,
        invoice.buyer.fiscal_code,
        invoice.buyer.address,
        invoice.buyer.country.name,
        invoice.buyer.bank_account,
        invoice.buyer.bank_name,
    ]
    return header


def render_header(pdf_canvas, header):
    # Assume A4 pagesize in portrait mode
    for i, textline in enumerate(header["left"]):
        pdf_canvas.setFont("Helvetica Neue" if i != 1 else "Helvetica-Bold", font_small)
        cx = left_margin
        cy = top_margin - i * row_height
        pdf_canvas.drawString(*to_cm(cx, cy), textline)

    for i, textline in enumerate(header["right"]):
        pdf_canvas.setFont("Helvetica Neue" if i != 1 else "Helvetica-Bold", font_small)
        cx = right_margin
        cy = top_margin - i * row_height
        pdf_canvas.drawRightString(*to_cm(cx, cy), textline)


def render_title(pdf_canvas, title):
    # Assume A4 pagesize in portrait mode
    pdf_canvas.setFont("Helvetica Neue", font_title)

    cx = page_width / 2
    cy = page_height - 8
    pdf_canvas.drawCentredString(*to_cm(cx, cy), title)

    return cy


def render_activity_subtitle(pdf_canvas, start_date, from_y):
    # Assume A4 pagesize in portrait mode
    pdf_canvas.setFont("Helvetica Neue", font_subtitle)

    cx = page_width / 2
    cy = from_y - (row_height + 2 * row_space)

    pdf_canvas.drawString(*to_cm(cx + row_space, cy), start_date.strftime("%B %Y"))
    cy -= row_height * 2

    return cy


def render_invoice_subtitle(pdf_canvas, invoice, from_y, international=False):
    # Assume A4 pagesize in portrait mode
    pdf_canvas.setFont("Helvetica Neue", font_subtitle)

    cx = page_width / 2
    cy = from_y - (row_height + 2 * row_space)

    pdf_canvas.drawRightString(*to_cm(cx - row_space, cy), "no:" if international else "nr:")
    pdf_canvas.drawString(*to_cm(cx + row_space, cy), invoice.series_number)
    cy -= row_height
    pdf_canvas.drawRightString(*to_cm(cx - row_space, cy), "date:" if international else "din:")
    pdf_canvas.drawString(*to_cm(cx + row_space, cy), invoice.issue_date.strftime("%d-%b-%Y"))
    cy -= row_height * 2

    return cy


def render_invoice_items(pdf_canvas, invoice, from_y, international=False):
    def draw_ruler(cy):
        pdf_canvas.setStrokeColorRGB(0, 0, 0)
        pdf_canvas.line(*to_cm(left_margin, cy - row_height / 2), *to_cm(right_margin, cy - row_height / 2))
        cy -= row_height * 2
        return cy

    # Assume A4 pagesize in portrait mode
    pdf_canvas.setFont("Helvetica-Bold", font_small)

    cx = page_width / 2

    cy = from_y - (row_height + 12 * row_space)
    headings = [
        ("No" if international else "Nr.", 2.5),
        ("Service description" if international else "Denumirea serviciului", 6),
        ("Qty" if international else "Cant.", 11),
        ("Unit" if international else "U.M.", 13),
        ("Unit price" if international else "Pret unitar", 15.5),
        ("Amount" if international else "Valoarea", 18.35),
    ]

    cy -= row_height / 2
    for h, x in headings:
        pdf_canvas.drawCentredString(x * cm, cy * cm, h)
    cy = draw_ruler(cy)

    # try to split description in two lines
    desc_line_1 = invoice.description
    desc_line_2 = ""
    if len(invoice.description) > 27:
        split_at = invoice.description.find(" ", 27)
        if split_at > 0:
            desc_line_1 = invoice.description[:split_at]
            desc_line_2 = invoice.description[split_at + 1 :]
    elif not invoice.description:
        desc_line_1 = "Software development services," if international else "Furnizare servicii software,"
        desc_line_2 = "acc. contract " if international else "cf. contract "
        desc_line_2 += "{} / {}".format(
            invoice.contract.registration_no, invoice.contract.registration_date.strftime("%d-%b-%Y")
        )

    pdf_canvas.setFont("Helvetica Neue", font_normal)
    pdf_canvas.drawCentredString(2.5 * cm, cy * cm, "1")
    pdf_canvas.drawCentredString(6 * cm, (cy + row_height * 0.4) * cm, desc_line_1)
    pdf_canvas.drawCentredString(6 * cm, (cy - row_height * 0.45) * cm, desc_line_2)

    pdf_canvas.drawCentredString(11 * cm, cy * cm, locale.str(invoice.quantity))
    unit = translate_units(invoice.unit, international)
    pdf_canvas.drawCentredString(13 * cm, cy * cm, unit)

    pdf_canvas.drawCentredString(
        15.5 * cm,
        cy * cm,
        locale.currency(
            invoice.unit_rate * (invoice.conversion_rate or 1), grouping=True, international=international
        ),
    )
    pdf_canvas.drawCentredString(
        18.35 * cm, cy * cm, locale.currency(invoice.value, grouping=True, international=international)
    )

    cy -= row_height / 2
    cy = draw_ruler(cy)

    pdf_canvas.setFont("Helvetica-Bold", font_small)
    pdf_canvas.drawCentredString(15.5 * cm, cy * cm, "Total" if international else "Total de plata")
    pdf_canvas.setFont("Helvetica-Bold", font_normal)
    pdf_canvas.drawCentredString(
        18.35 * cm, cy * cm, locale.currency(invoice.value, grouping=True, international=international)
    )

    cy -= row_height * 2
    if invoice.conversion_rate:
        pdf_canvas.setFont("Helvetica Neue", font_small)
        pdf_canvas.drawString(4 * cm, cy * cm, "Curs BNR")
        pdf_canvas.drawString(
            4 * cm,
            (cy - row_height) * cm,
            f'1 Euro = {locale.format_string("%.4f", invoice.conversion_rate)} lei',
        )

    cy -= row_height * 9
    if international:
        pdf_canvas.setFont("Helvetica Neue", font_tiny)
        pdf_canvas.drawCentredString(11 * cm, cy * cm, "* VAT reverse charge (dir. 2008/8/EC)")
        pdf_canvas.drawCentredString(
            11 * cm, (cy - row_height) * cm, "** non-taxable in Romania art. 268 (1)"
        )
        pdf_canvas.drawCentredString(
            11 * cm, (cy - 2 * row_height) * cm, "and art. 278 (2) of Romanian Fiscal Code"
        )
    else:
        pdf_canvas.drawCentredString(4 * cm, cy * cm, "Semnatura si")
        pdf_canvas.drawCentredString(4 * cm, (cy - row_height) * cm, "stampila furnizor")
        pdf_canvas.drawCentredString(17 * cm, cy * cm, "Semnatura")
        pdf_canvas.drawCentredString(17 * cm, (cy - row_height) * cm, "de primire")

        pdf_canvas.setFont("Helvetica Neue", font_tiny)
        pdf_canvas.drawCentredString(11 * cm, cy * cm, "Prezenta factura circula")
        pdf_canvas.drawCentredString(11 * cm, (cy - row_height) * cm, "fara semnatura si stampila,")
        pdf_canvas.drawCentredString(
            11 * cm, (cy - 2 * row_height) * cm, "cf. art. 319 (29) din Codul Fiscal"
        )

    return cy


def render_tasks_table(pdf_canvas, tasks, from_y, international=False):
    # table header
    headings = [
        ("Date" if international else "Data", 4),
        ("Project" if international else "Proiect", 7),
        ("Task" if international else "Activitate", 11),
        ("Hours" if international else "Ore", 18),
    ]
    pdf_canvas.setFont("Helvetica Neue", font_small)
    cy = from_y - 2 * (row_height + row_space)

    for h, x in headings:
        pdf_canvas.drawCentredString(x * cm, cy * cm, h)

    pdf_canvas.setStrokeColorRGB(0, 0, 0)
    pdf_canvas.line(
        *to_cm(left_margin + 1, cy - row_height / 2), *to_cm(right_margin - 1, cy - row_height / 2)
    )

    # contents
    pdf_canvas.setFont("Helvetica Neue", font_normal)
    cy -= row_height * 2 - row_space

    for task in tasks:
        # start_date, name, duration, client
        pdf_canvas.drawCentredString(*to_cm(4, cy), task["date"].strftime("%Y-%m-%d"))
        pdf_canvas.drawCentredString(*to_cm(7, cy), task["project"])
        pdf_canvas.drawString(*to_cm(9, cy), task["name"])
        pdf_canvas.drawCentredString(*to_cm(18, cy), str(int(task["duration"])))
        cy -= row_height + row_space

    pdf_canvas.line(
        *to_cm(left_margin + 1, cy + row_height / 2), *to_cm(right_margin - 1, cy + row_height / 2)
    )
    cy -= row_height

    # totals
    pdf_canvas.setFont("Helvetica-Bold", font_normal)
    pdf_canvas.drawRightString(*to_cm(18 - 2, cy), "Total")
    pdf_canvas.drawCentredString(*to_cm(18, cy), str(sum([t["duration"] for t in tasks])))

    return cy


def render_signatures(pdf_canvas, invoice, from_y=(page_height / 2), international=False):

    footer_left = [
        "Supplier" if international else "Furnizor:",
        "",
        invoice.seller.name,
        invoice.seller.owner_fullname,
    ]

    footer_right = [
        "Buyer:" if international else "Beneficiar:",
        "",
        invoice.buyer.name,
        invoice.buyer.owner_fullname,
    ]

    pdf_canvas.setFont("Helvetica Neue", font_normal)

    cy = from_y - 6 * (row_height + row_space)
    for t in footer_left:
        pdf_canvas.drawCentredString(*to_cm(6, cy), t)
        cy -= row_height + row_space

    cy = from_y - 6 * (row_height + row_space)
    for t in footer_right:
        pdf_canvas.drawCentredString(*to_cm(15, cy), t)
        cy -= row_height + row_space

    return


def render_watermark(pdf):
    import os

    pdf.setFont("Courier", font_tiny)
    pdf.drawRightString(*to_cm(right_margin, bottom_margin), ".. micro-tools.fibonet.ro ..")


def render_timesheet_ro(pdf, invoice, timesheet):
    header = create_ro_header_data(invoice)
    render_header(pdf, header)

    title = "Raport de activitate"
    bottom = render_title(pdf, title)
    bottom = render_activity_subtitle(pdf, timesheet["start_date"], from_y=bottom)

    bottom = render_tasks_table(pdf, timesheet["tasks"], from_y=bottom)
    bottom = render_signatures(pdf, invoice, from_y=bottom)
    render_watermark(pdf)

    pdf.showPage()


def render_timesheet_en(pdf, invoice, timesheet):
    header = create_en_header_data(invoice)
    render_header(pdf, header)

    title = "Timesheet report"
    bottom = render_title(pdf, title)
    bottom = render_activity_subtitle(pdf, timesheet["start_date"], from_y=bottom)

    bottom = render_tasks_table(pdf, timesheet["tasks"], from_y=bottom, international=True)
    bottom = render_signatures(pdf, invoice, from_y=bottom, international=True)
    render_watermark(pdf)

    pdf.showPage()


if __name__ == "__main__":
    print("This is a pure module, it cannot be executed.")
