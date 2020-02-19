import fpdf
import copy

# TODO: replace camel case with underscore


def render_activity_report(invoice):
    pdf = fpdf.FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial')
    initialX = pdf.get_x()
    initialY = pdf.get_y()
    tableColumnDateWidth = 25
    tableColumnClientCodeWidth = 35
    tableColumnDescriptionWidth = 80
    tableColumnHoursWidth = 10
    textWidth = 83.5

    def render_seller_info():
        pdf.set_font_size(9)
        pdf.cell(w=0,h=5,txt=f'Beneficiar: {invoice.seller.name}',align='L', ln=1)
        pdf.cell(w=0,h=5,txt=f'Nr. ORC: {invoice.seller.registration_id}',align='L',ln=1)
        pdf.cell(w=0,h=5,txt=f'CIF: {invoice.seller.fiscal_code}',align='L', ln=1)
        pdf.cell(w=0,h=5,txt=f'Sediul: {invoice.seller.address}',align='L',ln=1)
        pdf.cell(w=0,h=5,txt=f'Cont IBAN: {invoice.seller.bank_account}',align='L',ln=1)
        pdf.cell(w=0,h=5,txt=f'Banca: {invoice.seller.bank_name}',align='L',ln=1)

    def render_buyer_info():
        pdf.set_font_size(9)
        pdf.set_xy(initialX,initialY-1)
        pdf.cell(w=0, h=5, txt=f'Beneficiar: {invoice.buyer.name}', align='R', ln=1)
        pdf.cell(w=0,h=5, txt=f'Nr. ORC: {invoice.buyer.registration_id}',align='R',ln=1)
        pdf.cell(w=0,h=5,txt=f'CIF: {invoice.buyer.fiscal_code}',align='R', ln=1)
        pdf.cell(w=0,h=5,txt=f'Sediul: {invoice.buyer.address}',align='R',ln=1)
        pdf.cell(w=0,h=5,txt=f'Cont IBAN: {invoice.buyer.bank_account}',align='R',ln=1)
        pdf.cell(w=0,h=5,txt=f'Banca: {invoice.buyer.bank_name}',align='R',ln=1)

    def render_title():
        pdf.set_y(pdf.get_y()+20)
        pdf.set_font_size(18)
        pdf.cell(w=0,h=5,txt=f'Raport de activitate: {invoice.activity.start_date}', align='C', ln=1)

    def render_table_headings():
        pdf.set_font_size(12)
        pdf.set_font('Arial', 'B')
        pdf.set_y(pdf.get_y() + 20)
        
        pdf.set_x(initialX + 8)
        pdf.cell(w=tableColumnDateWidth,txt=f'Data',align='C')
        
        pdf.set_x(pdf.get_x() + 5)
        pdf.cell(w=tableColumnClientCodeWidth,txt=f'Cod client', align='C')

        pdf.set_x(pdf.get_x()+5)
        pdf.cell(w=tableColumnDescriptionWidth,txt=f'Descriere', align = 'C')

        pdf.set_x(pdf.get_x()+7)
        pdf.cell(w=tableColumnHoursWidth,txt=f'Ore',align = 'C')

    def render_tasks():
        length = tableColumnDateWidth + tableColumnClientCodeWidth + tableColumnDescriptionWidth + tableColumnHoursWidth + 38
        pdf.line(initialX+10,pdf.get_y()+5,length,pdf.get_y()+5)

        pdf.set_y(pdf.get_y()+8)
        pdf.set_font('Arial')
        pdf.set_font_size(12)
        for task in invoice.activity.tasks:
            # TODO: remove local copies use fully qualified properties
            date, project_id = task.date, task.project_id
            desc = task.name
            duration = task.duration

            pdf.set_x(initialX+8)
            pdf.cell(w=tableColumnDateWidth,txt=f'{date}',align='C')
            
            pdf.set_x(pdf.get_x()+5)
            pdf.cell(w=tableColumnClientCodeWidth,txt=f'{project_id}',align = 'C')

            pdf.set_x(pdf.get_x()+5)

            processedDescription = process_text_to_fit_width(pdf,desc,textWidth)
            current_y = pdf.get_y()
            for line in processedDescription:
                current_x = pdf.get_x()
                pdf.cell(w=tableColumnDescriptionWidth,txt=f'{line}', align = 'L', ln=1)
                pdf.set_y(pdf.get_y()+5)
                pdf.set_x(current_x)
                
                pdf.set_y(current_y)
                pdf.set_x(pdf.get_x() + tableColumnDescriptionWidth + 85)
                pdf.cell(w=tableColumnHoursWidth,txt=f'{duration}',align = 'C')
                pdf.set_y(pdf.get_y() + len(processedDescription)*5)

        pdf.line(initialX+10,pdf.get_y()-3,length,pdf.get_y()-3)

    def render_total():
        pdf.set_y(pdf.get_y()+5)
        pdf.set_x(tableColumnDateWidth + tableColumnClientCodeWidth + tableColumnDescriptionWidth+10)
        pdf.set_font(family='Arial',style='B')
        pdf.cell(w=20, txt=f'Total',align='C')

        # TODO: replace with activity.duration
        totalhours = 0
        for task in invoice.activity.tasks:
            totalhours += int(task.duration)
        
        pdf.set_x(pdf.get_x() + 5)
        pdf.cell(w=tableColumnHoursWidth, txt=f'{totalhours}')
        
        pdf.set_font(family='Arial')
    
    def render_seller_signature():

        current_y = pdf.get_y()
        pdf.set_xy(initialX + 30, pdf.get_y()+30)
        pdf.cell(w=20,txt=f'FURNIZOR: ', align = 'C')
        pdf.set_y(pdf.get_y() + 7)
        pdf.set_x(initialX + 30)
        pdf.cell(w=20,h=6,txt=f'{invoice.seller.name}',align = 'C', ln = 1)
        pdf.set_x(initialX + 30)
        pdf.cell(w=20,h=6,txt=f'Florinel',align = 'C', ln = 1)
        pdf.set_x(initialX + 30)
        pdf.cell(w=20,h=6,txt=f'L.S.',align = 'C', ln = 1)

        pdf.set_y(current_y)

    def render_buyer_signature():
        pdf.set_xy(initialX + 130, pdf.get_y()+30)
        pdf.cell(w=20,txt=f'BENEFICIAR: ', align = 'C')
        pdf.set_y(pdf.get_y() + 7)
        pdf.set_x(initialX + 130)
        pdf.cell(w=20,h=6,txt=f'{invoice.buyer.name}',align = 'C', ln = 1)
        pdf.set_x(initialX + 130)
        pdf.cell(w=20,h=6,txt=f'Mariusel',align = 'C', ln = 1)
        pdf.set_x(initialX + 130)
        pdf.cell(w=20,h=6,txt=f'L.S.',align = 'C', ln = 1)
    
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
    writeToPage(pdf)


def writeToPage(pdf):
    pdf.output("demo_pdf.pdf")