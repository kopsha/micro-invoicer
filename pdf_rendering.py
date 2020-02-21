import fpdf
import copy


def render_activity_report(invoice):
    pdf = fpdf.FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial')

    document_name = 'demo_pdf_activity_report.pdf'
    initialX = pdf.get_x()
    initialY = pdf.get_y()
    table_column_date_width = 25
    table_column_client_code_width = 35
    table_column_description_width = 80
    table_column_hours_width = 10
    text_width = 83.5

    def render_seller_info():
        pdf.set_font_size(9)
        pdf.cell(w=0, h=5, txt=f'Beneficiar: {invoice.seller.name}', align='L', ln=1)
        pdf.cell(w=0, h=5, txt=f'Nr. ORC: {invoice.seller.registration_id}', align='L', ln=1)
        pdf.cell(w=0, h=5, txt=f'CIF: {invoice.seller.fiscal_code}', align='L', ln=1)
        pdf.cell(w=0, h=5, txt=f'Sediul: {invoice.seller.address}', align='L', ln=1)
        pdf.cell(w=0, h=5, txt=f'Cont IBAN: {invoice.seller.bank_account}', align='L', ln=1)
        pdf.cell(w=0, h=5, txt=f'Banca: {invoice.seller.bank_name}', align='L', ln=1)

    def render_buyer_info():
        pdf.set_font_size(9)
        pdf.set_xy(initialX, initialY - 1)
        pdf.cell(w=0, h=5, txt=f'Beneficiar: {invoice.buyer.name}', align='R', ln=1)
        pdf.cell(w=0, h=5, txt=f'Nr. ORC: {invoice.buyer.registration_id}', align='R', ln=1)
        pdf.cell(w=0, h=5, txt=f'CIF: {invoice.buyer.fiscal_code}', align='R', ln=1)
        pdf.cell(w=0, h=5, txt=f'Sediul: {invoice.buyer.address}', align='R', ln=1)
        pdf.cell(w=0, h=5, txt=f'Cont IBAN: {invoice.buyer.bank_account}', align='R', ln=1)
        pdf.cell(w=0, h=5, txt=f'Banca: {invoice.buyer.bank_name}', align='R', ln=1)

    def render_title():
        pdf.set_y(pdf.get_y() + 20)
        pdf.set_font_size(18)
        pdf.cell(w=0, h=5, txt=f'Raport de activitate: {invoice.activity.start_date}', align='C', ln=1)

    def render_table_headings():
        pdf.set_font_size(12)
        pdf.set_font('Arial', 'B')
        pdf.set_y(pdf.get_y() + 20)
        
        pdf.set_x(initialX + 8)
        pdf.cell(w=table_column_date_width, txt=f'Data', align='C')
        
        pdf.set_x(pdf.get_x() + 5)
        pdf.cell(w=table_column_client_code_width, txt=f'Cod client', align='C')

        pdf.set_x(pdf.get_x() + 5)
        pdf.cell(w=table_column_description_width, txt=f'Descriere', align = 'C')

        pdf.set_x(pdf.get_x() + 7)
        pdf.cell(w=table_column_hours_width, txt=f'Ore', align = 'C')

    def render_tasks():
        length = table_column_date_width + table_column_client_code_width + table_column_description_width + table_column_hours_width + 38
        pdf.line(initialX + 10, pdf.get_y() + 5, length, pdf.get_y() + 5)

        pdf.set_y(pdf.get_y() + 8)
        pdf.set_font('Arial')
        pdf.set_font_size(12)
        for task in invoice.activity.tasks:
            pdf.set_x(initialX + 8)
            pdf.cell(w=table_column_date_width, txt=f'{task.date}', align='C')
            
            pdf.set_x(pdf.get_x() + 5)
            pdf.cell(w=table_column_client_code_width, txt=f'{task.project_id}', align = 'C')

            pdf.set_x(pdf.get_x() + 5)

            processed_description = process_text_to_fit_width(pdf, task.name, text_width)
            current_y = pdf.get_y()
            for line in processed_description:
                current_x = pdf.get_x()
                pdf.cell(w=table_column_description_width, txt=f'{line}', align = 'L', ln=1)
                pdf.set_y(pdf.get_y() + 5)
                pdf.set_x(current_x)
                
                pdf.set_y(current_y)
                pdf.set_x(pdf.get_x() + table_column_description_width + 85)
                pdf.cell(w=table_column_hours_width, txt=f'{task.duration}', align = 'C')
                pdf.set_y(pdf.get_y() + len(processed_description) * 5)

        pdf.line(initialX + 10, pdf.get_y() - 3, length, pdf.get_y() - 3)

    def render_total():
        pdf.set_y(pdf.get_y() + 5)
        pdf.set_x(table_column_date_width + table_column_client_code_width + table_column_description_width+10)
        pdf.set_font(family='Arial', style='B')
        pdf.cell(w=20, txt=f'Total', align='C')

        # TODO: replace with activity.duration
        totalhours = 0
        for task in invoice.activity.tasks:
            totalhours += int(task.duration)
        
        pdf.set_x(pdf.get_x() + 5)
        pdf.cell(w=table_column_hours_width, txt=f'{totalhours}')
        
        pdf.set_font(family='Arial')
    
    def render_seller_signature():

        current_y = pdf.get_y()
        pdf.set_xy(initialX + 30, pdf.get_y() + 30)
        pdf.cell(w=20, txt=f'FURNIZOR: ', align = 'C')
        pdf.set_y(pdf.get_y() + 7)
        pdf.set_x(initialX + 30)
        pdf.cell(w=20, h=6, txt=f'{invoice.seller.name}',align = 'C', ln = 1)
        pdf.set_x(initialX + 30)
        pdf.cell(w=20, h=6, txt=f'Florinel',align = 'C', ln = 1)
        pdf.set_x(initialX + 30)
        pdf.cell(w=20, h=6, txt=f'L.S.', align = 'C', ln = 1)

        pdf.set_y(current_y)

    def render_buyer_signature():
        pdf.set_xy(initialX + 130, pdf.get_y() + 30)
        pdf.cell(w=20, txt=f'BENEFICIAR: ', align = 'C')
        pdf.set_y(pdf.get_y() + 7)
        pdf.set_x(initialX + 130)
        pdf.cell(w=20, h=6, txt=f'{invoice.buyer.name}',align = 'C', ln = 1)
        pdf.set_x(initialX + 130)
        pdf.cell(w=20, h=6, txt=f'Mariusel', align = 'C', ln = 1)
        pdf.set_x(initialX + 130)
        pdf.cell(w=20, h=6, txt=f'L.S.', align = 'C', ln = 1)
    
    def process_text_to_fit_width(pdf, text,width):
        words = str(text).split()
        rows = []
        row = ''

        for word in words:
            next_row = ' '.join([row, word])
            if pdf.get_string_width(next_row) > width:
                # start a new row
                rows.append(row)
                row = next_row
        rows.append(row)

        return rows

    render_seller_info()
    render_buyer_info()
    render_title()
    render_table_headings()
    render_tasks()
    render_total()
    render_seller_signature()
    render_buyer_signature()
    write_to_page(pdf, document_name)


def render_invoice(invoice):
    pdf = fpdf.FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial')

    document_name = 'demo_pdf_invoice.pdf'
    initialX = pdf.get_x()
    initialY = pdf.get_y()

    def render_seller_info():
        pdf.set_font('Arial', style='B', size=9)
        pdf.cell(w=0, h=5, txt='Furnizor: ', ln=1)
        pdf.cell(w=0, h=5, txt='Nr. ORC: ', ln=1)
        pdf.cell(w=0, h=5, txt='CIF: ', ln=1)
        pdf.cell(w=0, h=5, txt='Sediul: ', ln=1)
        pdf.cell(w=0, h=5, txt='Cont: ', ln=1)
        pdf.cell(w=0, h=5, txt='Banca: ', ln=1)
        rendered_seller_length = pdf.get_string_width('Furnizor:')
        rendered_registration_id_length = pdf.get_string_width('Nr. ORC:')
        rendered_fiscal_code_length = pdf.get_string_width('CIF:')
        rendered_address_length = pdf.get_string_width('Sediul:')
        rendered_bank_account_length = pdf.get_string_width('Cont:')
        rendered_bank_name_length = pdf.get_string_width('Banca:')

        pdf.set_font('Arial', style='')
        pdf.set_xy(initialX + rendered_seller_length + 2, initialY)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.name}', ln=1)
        pdf.set_x(initialX + rendered_registration_id_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.registration_id}', ln=1)
        pdf.set_x(initialX + rendered_fiscal_code_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.fiscal_code}', ln=1)
        pdf.set_x(initialX + rendered_address_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.address}', ln=1)
        pdf.set_x(initialX + rendered_bank_account_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.bank_account}', ln=1)
        pdf.set_x(initialX + rendered_bank_name_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.bank_name}', ln=1)

    def render_buyer_info():
        local_offset = initialX + 105

        pdf.set_xy(local_offset, initialY)
        pdf.set_font('Arial', style='B', size=9)
        pdf.cell(w=0, h=5, txt='Cumparator: ', ln=1)
        pdf.set_x(local_offset)
        pdf.cell(w=0, h=5, txt='Nr. ORC: ', ln=1)
        pdf.set_x(local_offset)
        pdf.cell(w=0, h=5, txt='CIF: ', ln=1)
        pdf.set_x(local_offset)
        pdf.cell(w=0, h=5, txt='Sediul: ', ln=1)
        pdf.set_x(local_offset)
        pdf.cell(w=0, h=5, txt='Cont: ', ln=1)
        pdf.set_x(local_offset)
        pdf.cell(w=0, h=5, txt='Banca: ', ln=1)

        rendered_buyer_length = pdf.get_string_width('Cumparator:')
        rendered_registration_id_length = pdf.get_string_width('Nr. ORC:')
        rendered_fiscal_code_length = pdf.get_string_width('CIF:')
        rendered_address_length = pdf.get_string_width('Sediul:')
        rendered_bank_account_length = pdf.get_string_width('Cont:')
        rendered_bank_name_length = pdf.get_string_width('Banca:')

        pdf.set_font('Arial', style='')
        pdf.set_xy(local_offset + rendered_buyer_length + 2, initialY)
        pdf.cell(w=0, h=5, txt=f'{invoice.buyer.name}', ln=1)
        pdf.set_x(local_offset + rendered_registration_id_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.seller.registration_id}', ln=1)
        pdf.set_x(local_offset + rendered_fiscal_code_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.buyer.fiscal_code}', ln=1)
        pdf.set_x(local_offset + rendered_address_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.buyer.address}', ln=1)
        pdf.set_x(local_offset + rendered_bank_account_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.buyer.bank_account}', ln=1)
        pdf.set_x(local_offset + rendered_bank_name_length + 2)
        pdf.cell(w=0, h=5, txt=f'{invoice.buyer.bank_name}', ln=1)
    def render_title():
        local_offset = initialX + 105
        pdf.set_font('Arial', style='', size=14)
        pdf.set_xy(initialX,initialY+40)
        pdf.cell(w=0,h=7,txt='FACTURA FISCALA', align='C', ln=1)
        pdf.set_font('Arial', style='', size=9)
        pdf.set_x(local_offset - pdf.get_string_width(f'Seria: {invoice.series} {invoice.number}                            din {invoice.activity.start_date}')/2)
        pdf.cell(w=0,h=5,txt=f'Seria: {invoice.series} {invoice.number}                            din {invoice.activity.start_date}')

    def render_horizontal_lines():
        pdf.set_xy(initialX, pdf.get_y()+20)
        pdf.line(initialX,pdf.get_y(),initialX+190,pdf.get_y())

        pdf.set_y(pdf.get_y()+8)
        pdf.line(initialX,pdf.get_y(),initialX+190,pdf.get_y())

        pdf.set_y(pdf.get_y()+1.1)
        pdf.line(initialX,pdf.get_y(),initialX+190,pdf.get_y())
    def render_vertical_lines():
        pass
    
    def render_table_headings():
        pass

    def render_table_data():
        pass
    
    render_seller_info()
    render_buyer_info()
    render_title()
    render_horizontal_lines()
    render_table_headings()
    render_table_data()
    render_vertical_lines()
    write_to_page(pdf,document_name)

def write_to_page(pdf, document_name):
    pdf.output(document_name)