import fpdf
import copy
def render_activity_report(invoice):
    pdf = fpdf.FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial")
    initialX = pdf.get_x()
    initialY = pdf.get_y()
    tableColumnDateWidth = 25
    tableColumnClientCodeWidth = 35
    tableColumnDescriptionWidth = 80
    tableColumnHoursWidth = 10

    create_seller_info(pdf,invoice)
    create_buyer_info(pdf,invoice,
                    initialX,
                    initialY
                    )
    create_title(pdf,invoice)
    create_headtypes(pdf,invoice,
                    tableColumnDateWidth, 
                    tableColumnClientCodeWidth,
                    tableColumnDescriptionWidth,
                    tableColumnHoursWidth,
                    initialX,
                    initialY
                    )
    create_invoice_with_data(pdf,invoice,
                    tableColumnDateWidth, 
                    tableColumnClientCodeWidth,
                    tableColumnDescriptionWidth,
                    tableColumnHoursWidth,
                    initialX,
                    initialY)
    create_total(pdf,invoice,
                tableColumnDateWidth, 
                tableColumnClientCodeWidth,
                tableColumnDescriptionWidth,
                tableColumnHoursWidth,
                )
    create_seller_signature(pdf,invoice,
                    tableColumnDateWidth, 
                    tableColumnClientCodeWidth,
                    tableColumnDescriptionWidth,
                    tableColumnHoursWidth,
                    initialX,
                    initialY)
    create_buyer_signature(pdf,invoice,
                    tableColumnDateWidth, 
                    tableColumnClientCodeWidth,
                    tableColumnDescriptionWidth,
                    tableColumnHoursWidth,
                    initialX,
                    initialY)
    writeToPage(pdf)

def create_seller_info(pdf,invoice):
    pdf.set_font_size(9)
    pdf.cell(w=0,h=5,txt=f'Beneficiar: {invoice.seller.name}',align='L', ln=1)
    pdf.cell(w=0,h=5,txt=f'Nr. ORC: {invoice.seller.registration_id}',align='L',ln=1)
    pdf.cell(w=0,h=5,txt=f'CIF: {invoice.seller.fiscal_code}',align='L', ln=1)
    pdf.cell(w=0,h=5,txt=f'Sediul: {invoice.seller.address}',align='L',ln=1)
    pdf.cell(w=0,h=5,txt=f'Cont IBAN: {invoice.seller.bank_account}',align='L',ln=1)
    pdf.cell(w=0,h=5,txt=f'Banca: {invoice.seller.bank_name}',align='L',ln=1)

def create_buyer_info(pdf,
                    invoice,
                    initialX,
                    initialY
                    ):
    pdf.set_font_size(9)
    pdf.set_xy(initialX,initialY-1)
    pdf.cell(w=0,h=5,txt=f'Beneficiar: {invoice.buyer.name}',align='R', ln=1)
    pdf.cell(w=0,h=5,txt=f'Nr. ORC: {invoice.buyer.registration_id}',align='R',ln=1)
    pdf.cell(w=0,h=5,txt=f'CIF: {invoice.buyer.fiscal_code}',align='R', ln=1)
    pdf.cell(w=0,h=5,txt=f'Sediul: {invoice.buyer.address}',align='R',ln=1)
    pdf.cell(w=0,h=5,txt=f'Cont IBAN: {invoice.buyer.bank_account}',align='R',ln=1)
    pdf.cell(w=0,h=5,txt=f'Banca: {invoice.buyer.bank_name}',align='R',ln=1)

def create_title(pdf,invoice):
    pdf.set_y(pdf.get_y()+20)
    pdf.set_font_size(18)
    pdf.cell(w=0,h=5,txt=f'Raport de activitate: {invoice.activity.start_date}', align='C', ln=1)

def create_headtypes(pdf,
                    invoice,
                    tableColumnDateWidth, 
                    tableColumnClientCodeWidth,
                    tableColumnDescriptionWidth,
                    tableColumnHoursWidth,
                    initialX,
                    initialY):
    pdf.set_font_size(12)
    pdf.set_font('Arial','B')
    pdf.set_y(pdf.get_y()+20)
        
    pdf.set_x(initialX+8)
    pdf.cell(w=tableColumnDateWidth,txt=f'Data',align='C')
        
    pdf.set_x(pdf.get_x()+5)
    pdf.cell(w=tableColumnClientCodeWidth,txt=f'Cod client',align = 'C')

    pdf.set_x(pdf.get_x()+5)
    pdf.cell(w=tableColumnDescriptionWidth,txt=f'Descriere', align = 'C')

    pdf.set_x(pdf.get_x()+7)
    pdf.cell(w=tableColumnHoursWidth,txt=f'Ore',align = 'C')

def create_invoice_with_data(pdf,
                            invoice,
                            tableColumnDateWidth, 
                            tableColumnClientCodeWidth,
                            tableColumnDescriptionWidth,
                            tableColumnHoursWidth,
                            initialX,
                            initialY
                            ):
    length = tableColumnDateWidth + tableColumnClientCodeWidth + tableColumnDescriptionWidth + tableColumnHoursWidth + 38
    pdf.line(initialX+10,pdf.get_y()+5,length,pdf.get_y()+5)

    pdf.set_y(pdf.get_y()+8)
    pdf.set_font('Arial')
    pdf.set_font_size(12)
    for task in invoice.activity.tasks:
        date = task.date
        project_id = task.project_id
        desc = task.name
        duration = task.duration

        pdf.set_x(initialX+8)
        pdf.cell(w=tableColumnDateWidth,txt=f'{date}',align='C')
            
        pdf.set_x(pdf.get_x()+5)
        pdf.cell(w=tableColumnClientCodeWidth,txt=f'{project_id}',align = 'C')

        pdf.set_x(pdf.get_x()+5)

        processedDescription = process_description(pdf,desc)
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
    
def process_description(pdf,text):
    words = str(text).split()
    rows = []
    row = ''
    for word in words:
        next_row = ' '.join([row, word])
        isLast = False
        isFitting = False

        if  pdf.get_string_width(next_row) <= 83.50:
            isFitting = True
        if word == words[-1]:
            isLast = True

        if isFitting:
            row = next_row
        if isLast or not isFitting:
            rows.append(row)
            row = ''
    return rows

def create_total(pdf,
                invoice,
                tableColumnDateWidth, 
                tableColumnClientCodeWidth,
                tableColumnDescriptionWidth,
                tableColumnHoursWidth,
                ):
    pdf.set_y(pdf.get_y()+5)
    pdf.set_x(tableColumnDateWidth + tableColumnClientCodeWidth + tableColumnDescriptionWidth+10)
    pdf.set_font(family='Arial',style='B')
    pdf.cell(w=20, txt=f'Total',align='C')

    totalhours = 0
    for task in invoice.activity.tasks:
        totalhours += int(task.duration)
        
    pdf.set_x(pdf.get_x() + 5)
    pdf.cell(w=tableColumnHoursWidth, txt=f'{totalhours}')
        
    pdf.set_font(family='Arial')
    
def create_seller_signature(pdf,
                            invoice,
                            tableColumnDateWidth, 
                            tableColumnClientCodeWidth,
                            tableColumnDescriptionWidth,
                            tableColumnHoursWidth,
                            initialX,
                            initialY
                            ):

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

def create_buyer_signature(pdf,
                            invoice,
                            tableColumnDateWidth, 
                            tableColumnClientCodeWidth,
                            tableColumnDescriptionWidth,
                            tableColumnHoursWidth,
                            initialX,
                            initialY
                            ):
    pdf.set_xy(initialX + 130, pdf.get_y()+30)
    pdf.cell(w=20,txt=f'BENEFICIAR: ', align = 'C')
    pdf.set_y(pdf.get_y() + 7)
    pdf.set_x(initialX + 130)
    pdf.cell(w=20,h=6,txt=f'{invoice.buyer.name}',align = 'C', ln = 1)
    pdf.set_x(initialX + 130)
    pdf.cell(w=20,h=6,txt=f'Mariusel',align = 'C', ln = 1)
    pdf.set_x(initialX + 130)
    pdf.cell(w=20,h=6,txt=f'L.S.',align = 'C', ln = 1)
        

def writeToPage(pdf):
    pdf.output("demo_pdf.pdf")