from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from io import BytesIO

from .micro_models import *


page_width, page_height = (21.0, 29.7)
row_height = 0.42
row_space = 0.1
top_margin = page_height - 1.1
left_margin = 1.4
right_margin = page_width - 1.1


def to_cm(xu, yu):
	return (xu*cm,yu*cm)


def translate_month(date):
	all_months = [
		'Ianuarie',
		'Februarie',
		'Martie',
		'Aprilie',
		'Mai',
		'Iunie',
		'Iulie',
		'August',
		'Septembrie',
		'Octombrie',
		'Noiembrie',
		'Decembrie'
	]

	return all_months[date.month-1]


def render_header(pdf_canvas, invoice):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont("Helvetica", 9)
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
	pdf_canvas.setFont("Helvetica", 18)

	cx = page_width/2
	cy = page_height - 6
	pdf_canvas.drawCentredString(*to_cm(cx,cy), title)

	return cy

def render_subtitle(pdf_canvas, text, from_y):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont("Helvetica", 15)

	cx = page_width/2

	cy = from_y - (row_height + 2 * row_space)
	pdf_canvas.drawCentredString(*to_cm(cx,cy), text)

	return cy


def render_invoice_items(pdf_canvas, invoice, from_y):
	# Assume A4 pagesize in portrait mode 
	pdf_canvas.setFont("Helvetica", 9)

	cx = page_width/2

	cy = from_y - (row_height + 8 * row_space)
	headings = [
		('Nr.', 2),
		('Denumirea produsului / serviciului', 6),
		('U.M.', 13),
		('Cant.', 14.25),
		('Pret unitar', 16),
		('Valoarea', 18.65),
	]

	pdf_canvas.setStrokeColorRGB(0,0,0)
	pdf_canvas.line(*to_cm(left_margin, cy-row_height/2), *to_cm(right_margin, cy-row_height/2))

	for h, x in headings:
		pdf_canvas.drawCentredString(x*cm, cy*cm, h)
	cy -= row_height * 2

	pdf_canvas.drawCentredString(2*cm, cy*cm, '1')
	pdf_canvas.drawCentredString(6*cm, cy*cm, 'Furnizare servicii software')
	pdf_canvas.drawCentredString(13*cm, cy*cm, 'ore')
	pdf_canvas.drawCentredString(14.25*cm, cy*cm, f'{invoice.activity.duration}')
	pdf_canvas.drawCentredString(16*cm, cy*cm, f'{invoice.hourly_rate * invoice.conversion_rate:.2f} lei')
	pdf_canvas.drawCentredString(18.65*cm, cy*cm, f'{invoice.value:.2f} lei')

	return cy

def render_tasks_table(pdf_canvas, activity, from_y):
	# table header
	headings = [
		('Data', 4),
		('Cod client', 7),
		('Descriere', 11),
		('Ore', 18),
	]
	pdf_canvas.setFont("Helvetica-Bold", 11)
	cy = from_y - 4 * (row_height + row_space)


	for h,x in headings:
		pdf_canvas.drawCentredString(x*cm, cy*cm, h)

	pdf_canvas.setStrokeColorRGB(0,0,0)
	pdf_canvas.line(*to_cm(left_margin+1,cy-row_height/2), *to_cm(right_margin-1,cy-row_height/2))

	# contents
	pdf_canvas.setFont("Helvetica", 11)
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
	pdf_canvas.setFont("Helvetica-Bold", 11)
	pdf_canvas.drawRightString(*to_cm(18-2,cy), "Total")
	pdf_canvas.drawCentredString(*to_cm(18,cy), str(activity.duration))

	return cy


def render_signatures(pdf_canvas, invoice, from_y=(page_height/2)):

	footer_left = [
		'Furnizor:',
		'',
		invoice.seller.name,
		invoice.seller.owner_fullname,
		'L.S.',
	]

	footer_right = [
		'Beneficiar:',
		'',
		invoice.buyer.name,
		invoice.buyer.owner_fullname,
		'L.S.',
	]

	pdf_canvas.setFont("Helvetica", 11)

	cy = from_y - 6*(row_height + row_space)
	for t in footer_left:
		pdf_canvas.drawCentredString( *to_cm(6, cy), t)
		cy -= (row_height + row_space)

	cy = from_y - 6*(row_height + row_space)
	for t in footer_right:
		pdf_canvas.drawCentredString( *to_cm(15, cy), t)
		cy -= (row_height + row_space)

	return


def render_activity_page(pdf, invoice):
	start_date = invoice.activity.start_date
	month_name = f'{translate_month(start_date)} {start_date.strftime("%Y")}'
	title = f'Raport de activitate: {month_name}'

	render_header(pdf, invoice)
	bottom = render_title(pdf, title)
	bottom = render_tasks_table(pdf, invoice.activity, from_y=bottom)
	bottom = render_signatures(pdf, invoice, from_y=bottom)

	pdf.showPage()


def render_invoice_page(pdf, invoice):
	title = f'FACTURA {invoice.series_number}'
	subtitle = f'din {invoice.activity.start_date.isoformat()}'

	render_header(pdf, invoice)
	bottom = render_title(pdf, title)
	bottom = render_subtitle(pdf, subtitle, from_y=bottom)
	bottom = render_invoice_items(pdf, invoice, from_y=bottom)

	pdf.showPage()

def write_invoice_pdf(invoice):
	write_to = BytesIO()
	pdf = canvas.Canvas(filename=write_to, pagesize=A4)

	render_invoice_page(pdf, invoice)
	render_activity_page(pdf, invoice)

	pdf.save()
	write_to.seek(0)
	
	return write_to
