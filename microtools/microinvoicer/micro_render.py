from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from io import BytesIO

import locale
import time

from .micro_models import *


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

def to_cm(xu, yu):
	return (xu*cm,yu*cm)

def render_header(pdf_canvas, invoice):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont('Helvetica', font_small)
	header_left = [
		f'Furnizor: {invoice.seller.name}',
		f'Nr. ORC: {invoice.seller.registration_id}',
		f'CUI: {invoice.seller.fiscal_code}',
		f'Sediul: {invoice.seller.address}',
		f'Cont IBAN: {invoice.seller.bank_account}',
		f'Banca: {invoice.seller.bank_name}',
	]
	header_right = [
		f'Beneficiar: {invoice.buyer.name}',
		f'Nr. ORC: {invoice.buyer.registration_id}',
		f'CIF: {invoice.buyer.fiscal_code}',
		f'Sediul: {invoice.buyer.address}',
		f'Cont IBAN: {invoice.buyer.bank_account}',
		f'Banca: {invoice.buyer.bank_name}',
	]

	for i,textline in enumerate(header_left):
		cx = left_margin
		cy = top_margin - i*row_height
		pdf_canvas.drawString( *to_cm(cx,cy), textline)

	for i,textline in enumerate(header_right):
		cx = right_margin
		cy = top_margin - i*row_height
		pdf_canvas.drawRightString( *to_cm(cx,cy), textline)

def render_title(pdf_canvas, title):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont('Helvetica', font_title)

	cx = page_width/2
	cy = page_height - 8
	pdf_canvas.drawCentredString(*to_cm(cx,cy), title)

	return cy

def render_activity_subtitle(pdf_canvas, activity, from_y):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont('Helvetica', font_subtitle)

	cx = page_width/2
	cy = from_y - (row_height + 2 * row_space)

	pdf_canvas.drawString(*to_cm(cx + row_space,cy), activity.start_date.strftime("%B %Y"))
	cy -= row_height*2

	return cy


def render_invoice_subtitle(pdf_canvas, invoice, from_y):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont('Helvetica', font_subtitle)

	cx = page_width/2
	cy = from_y - (row_height + 2 * row_space)

	pdf_canvas.drawRightString(*to_cm(cx - row_space,cy), 'nr:')
	pdf_canvas.drawString(*to_cm(cx + row_space,cy), invoice.series_number)
	cy -= row_height
	pdf_canvas.drawRightString(*to_cm(cx - row_space,cy), 'din:')
	pdf_canvas.drawString(*to_cm(cx + row_space,cy), invoice.publish_date.strftime("%d-%b-%Y"))
	cy -= row_height*2

	return cy


def render_invoice_items(pdf_canvas, invoice, from_y):

	def draw_ruler(cy):
		pdf_canvas.setStrokeColorRGB(0,0,0)
		pdf_canvas.line(*to_cm(left_margin, cy-row_height/2), *to_cm(right_margin, cy-row_height/2))
		cy -= row_height * 2
		return cy

	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont('Helvetica-Bold', font_small)

	cx = page_width/2

	cy = from_y - (row_height + 12 * row_space)
	headings = [
		('Nr.', 2.5),
		('Denumirea produsului / serviciului', 6),
		('Cant.', 11),
		('U.M.', 13),
		('Pret unitar', 15.5),
		('Valoarea', 18.35),
	]

	cy -= row_height / 2
	for h, x in headings:
		pdf_canvas.drawCentredString(x*cm, cy*cm, h)
	cy = draw_ruler(cy)

	pdf_canvas.setFont('Helvetica', font_normal)
	pdf_canvas.drawCentredString(2.5*cm, cy*cm, '1')
	pdf_canvas.drawCentredString(6*cm, (cy + row_height*0.4)*cm, 'Furnizare servicii software,')
	pdf_canvas.drawCentredString(6*cm, (cy - row_height*0.45)*cm, f' cf. contract {invoice.contract_registry_id} din {invoice.contract_registry_date.strftime("%d-%b-%Y")}')

	pdf_canvas.drawCentredString(11*cm, cy*cm, locale.str(invoice.activity.duration))
	pdf_canvas.drawCentredString(13*cm, cy*cm, 'ore')

	pdf_canvas.drawCentredString(15.5*cm, cy*cm, locale.currency(invoice.hourly_rate * invoice.conversion_rate))
	pdf_canvas.drawCentredString(18.35*cm, cy*cm, locale.currency(invoice.value, grouping=True))

	cy -= row_height / 2
	cy = draw_ruler(cy)

	pdf_canvas.setFont('Helvetica-Bold', font_small)
	pdf_canvas.drawCentredString(15.5*cm, cy*cm, 'Total de plata')
	pdf_canvas.setFont('Helvetica-Bold', font_normal)
	pdf_canvas.drawCentredString(18.35*cm, cy*cm, locale.currency(invoice.value, grouping=True))


	cy -= row_height * 2
	pdf_canvas.setFont('Helvetica', font_small)
	pdf_canvas.drawString(4*cm, cy*cm, 'Curs BNR')
	pdf_canvas.drawString(4*cm, (cy-row_height)*cm, f'1 Euro = {locale.format_string("%.4f", invoice.conversion_rate)} lei')

	cy -= row_height * 9
	pdf_canvas.drawCentredString(4*cm, cy*cm, 'Semnatura si')
	pdf_canvas.drawCentredString(4*cm, (cy-row_height)*cm, 'stampila furnizor')
	pdf_canvas.drawCentredString(17*cm, cy*cm, 'Semnatura')
	pdf_canvas.drawCentredString(17*cm, (cy-row_height)*cm, 'de primire')

	pdf_canvas.setFont('Helvetica', font_tiny)
	pdf_canvas.drawCentredString(11*cm, cy*cm, 'Prezenta factura circula')
	pdf_canvas.drawCentredString(11*cm, (cy-row_height)*cm, 'fara semnatura si stampila,')
	pdf_canvas.drawCentredString(11*cm, (cy-2*row_height)*cm, 'cf. art. 319 (29) din Codul Fiscal')


	return cy

def render_tasks_table(pdf_canvas, activity, from_y):
	# table header
	headings = [
		('Data', 4),
		('Cod client', 7),
		('Descriere', 11),
		('Ore', 18),
	]
	pdf_canvas.setFont('Helvetica', font_small)
	cy = from_y - 2 * (row_height + row_space)


	for h,x in headings:
		pdf_canvas.drawCentredString(x*cm, cy*cm, h)

	pdf_canvas.setStrokeColorRGB(0,0,0)
	pdf_canvas.line(*to_cm(left_margin+1,cy-row_height/2), *to_cm(right_margin-1,cy-row_height/2))

	# contents
	pdf_canvas.setFont('Helvetica', font_normal)
	cy -= row_height*2

	for task in activity.tasks:
		#start_date, name, duration, client
		pdf_canvas.drawCentredString(*to_cm(4,cy), task.date.strftime("%Y-%m-%d"))
		pdf_canvas.drawCentredString(*to_cm(7,cy), task.project_id)
		pdf_canvas.drawString(*to_cm(9,cy), task.name)
		pdf_canvas.drawCentredString(*to_cm(18,cy), str(int(task.duration)))
		cy -= (row_height + row_space)

	pdf_canvas.line(*to_cm(left_margin+1,cy+row_height/2), *to_cm(right_margin-1,cy+row_height/2))
	cy -= row_height

	# totals
	pdf_canvas.setFont('Helvetica-Bold', font_normal)
	pdf_canvas.drawRightString(*to_cm(18-2,cy), "Total")
	pdf_canvas.drawCentredString(*to_cm(18,cy), str(activity.duration))

	return cy


def render_signatures(pdf_canvas, invoice, from_y=(page_height/2)):

	footer_left = [
		'Furnizor:',
		'',
		invoice.seller.name,
		invoice.seller.owner_fullname,
		'',
		'L.S.',
	]

	footer_right = [
		'Beneficiar:',
		'',
		invoice.buyer.name,
		invoice.buyer.owner_fullname,
		'',
		'L.S.',
	]

	pdf_canvas.setFont('Helvetica', font_normal)

	cy = from_y - 6*(row_height + row_space)
	for t in footer_left:
		pdf_canvas.drawCentredString( *to_cm(6, cy), t)
		cy -= (row_height + row_space)

	cy = from_y - 6*(row_height + row_space)
	for t in footer_right:
		pdf_canvas.drawCentredString( *to_cm(15, cy), t)
		cy -= (row_height + row_space)

	return


def render_watermark(pdf):
	import os
	pdf.setFont('Courier', font_tiny)
	pdf.drawRightString( *to_cm(right_margin, bottom_margin), '.. micro-tools.fortech.ro ..' )

def render_activity_page(pdf, invoice):
	title = 'Raport de activitate'

	render_header(pdf, invoice)
	bottom = render_title(pdf, title)
	bottom = render_activity_subtitle(pdf, invoice.activity, from_y=bottom)
	bottom = render_tasks_table(pdf, invoice.activity, from_y=bottom)
	bottom = render_signatures(pdf, invoice, from_y=bottom)
	render_watermark(pdf)

	pdf.showPage()


def render_invoice_page(pdf, invoice):
	title = f'FACTURA'

	render_header(pdf, invoice)
	bottom = render_title(pdf, title)
	bottom = render_invoice_subtitle(pdf, invoice, from_y=bottom)
	bottom = render_invoice_items(pdf, invoice, from_y=bottom)

	render_watermark(pdf)
	pdf.showPage()

def write_invoice_pdf(invoice):
	locale.setlocale(locale.LC_ALL, 'ro_RO')

	write_buffer = BytesIO()
	pdf = canvas.Canvas(filename=write_buffer, pagesize=A4)
	pdf.setAuthor('python@micro-tools.fortech.ro')

	render_invoice_page(pdf, invoice)
	render_activity_page(pdf, invoice)

	pdf.save()
	write_buffer.seek(0)
	
	return write_buffer
