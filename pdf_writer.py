import fpdf
import copy
class PdfGenerator:
    def __init__(self, invoice):
        self.invoice = invoice
        self.pdf = fpdf.FPDF(orientation='P', unit='mm', format='A4')
        self.pdf.add_page()
        self.pdf.set_font("Arial")

        self.initialX = self.pdf.get_x()
        self.initialY = self.pdf.get_y()

        self.tableColumnDateWidth = 25
        self.tableColumnClientCodeWidth = 35
        self.tableColumnDescriptionWidth = 80
        self.tableColumnHoursWidth = 10

    def generatePdf(self):
        self.create_seller_info()
        self.create_buyer_info()
        self.create_title()
        self.create_headtypes()
        self.create_invoice_with_data()
        self.create_total()
        self.create_seller_signature()
        self.create_buyer_signature()
        self.writeToPage()

    def create_seller_info(self):
        self.pdf.set_font_size(9)
        output_string = f''
        output_string += f'FURNIZOR: {self.invoice.seller.name} \n'
        output_string += f'Nr. ORC: {self.invoice.seller.registration_id} \n'
        output_string += f'CUI: {self.invoice.seller.fiscal_code} \n'
        output_string += f'Sediul: {self.invoice.seller.address} \n'
        output_string += f'Cont IBAN: {self.invoice.seller.bank_account} \n'
        output_string += f'Banca: {self.invoice.seller.bank_name}'
        self.pdf.multi_cell(w=0,h=5,txt=output_string,align='L')

    def create_buyer_info(self):
        self.pdf.set_font_size(9)
        self.pdf.set_xy(self.initialX,self.initialY)
        self.pdf.cell(w=0,h=5,txt=f'Beneficiar: {self.invoice.buyer.name}',align='R', ln=1)
        self.pdf.cell(w=0,h=5,txt=f'Nr. ORC: {self.invoice.buyer.registration_id}',align='R',ln=1)
        self.pdf.cell(w=0,h=5,txt=f'CIF: {self.invoice.buyer.fiscal_code}',align='R', ln=1)
        self.pdf.cell(w=0,h=5,txt=f'Sediul: {self.invoice.buyer.address}',align='R',ln=1)
        self.pdf.cell(w=0,h=5,txt=f'Cont IBAN: {self.invoice.buyer.bank_account}',align='R',ln=1)
        self.pdf.cell(w=0,h=5,txt=f'Banca: {self.invoice.buyer.bank_name}',align='R',ln=1)

    def create_title(self):
        self.pdf.set_y(self.pdf.get_y()+20)
        self.pdf.set_font_size(18)
        self.pdf.cell(w=0,h=5,txt=f'Raport de activitate: {self.invoice.activity.start_date}', align='C', ln=1)

    def create_headtypes(self):
        self.pdf.set_font_size(12)
        self.pdf.set_font('Arial','B')
        self.pdf.set_y(self.pdf.get_y()+20)
        
        self.pdf.set_x(self.initialX+8)
        self.pdf.cell(w=self.tableColumnDateWidth,txt=f'Data',align='C')
        
        self.pdf.set_x(self.pdf.get_x()+5)
        self.pdf.cell(w=self.tableColumnClientCodeWidth,txt=f'Cod client',align = 'C')

        self.pdf.set_x(self.pdf.get_x()+5)
        self.pdf.cell(w=self.tableColumnDescriptionWidth,txt=f'Descriere', align = 'C')

        self.pdf.set_x(self.pdf.get_x()+7)
        self.pdf.cell(w=self.tableColumnHoursWidth,txt=f'Ore',align = 'C')

    def create_invoice_with_data(self):
        length = self.tableColumnDateWidth + self.tableColumnClientCodeWidth + self.tableColumnDescriptionWidth + self.tableColumnHoursWidth + 38
        self.pdf.line(self.initialX+10,self.pdf.get_y()+5,length,self.pdf.get_y()+5)

        self.pdf.set_y(self.pdf.get_y()+8)
        self.pdf.set_font('Arial')
        self.pdf.set_font_size(12)
        for task in self.invoice.activity.tasks:
            date = task.date
            project_id = task.project_id
            desc = task.name
            duration = task.duration

            self.pdf.set_x(self.initialX+8)
            self.pdf.cell(w=self.tableColumnDateWidth,txt=f'{date}',align='C')
            
            self.pdf.set_x(self.pdf.get_x()+5)
            self.pdf.cell(w=self.tableColumnClientCodeWidth,txt=f'{project_id}',align = 'C')

            self.pdf.set_x(self.pdf.get_x()+5)

            processedDescription = self.process_description(desc)
            current_y = self.pdf.get_y()
            for line in processedDescription:
                current_x = self.pdf.get_x()
                self.pdf.cell(w=self.tableColumnDescriptionWidth,txt=f'{line}', align = 'L', ln=1)
                self.pdf.set_y(self.pdf.get_y()+5)
                self.pdf.set_x(current_x)
                
            self.pdf.set_y(current_y)
            self.pdf.set_x(self.pdf.get_x() + self.tableColumnDescriptionWidth + 85)
            self.pdf.cell(w=self.tableColumnHoursWidth,txt=f'{duration}',align = 'C')
            self.pdf.set_y(self.pdf.get_y() + len(processedDescription)*5)

        self.pdf.line(self.initialX+10,self.pdf.get_y()-3,length,self.pdf.get_y()-3)
    
    def process_description(self,text):
        words = str(text).split()
        rows = []
        row = ''
        for word in words:
            next_row = ' '.join([row, word])
            isLast = False
            isFitting = False

            if self.pdf.get_string_width(next_row) <= 83.50:
                isFitting = True
            if word == words[-1]:
                isLast = True
            
            if isFitting:
                row = next_row
            if isLast or not isFitting:
                rows.append(row)
                row = ''
        return rows

    def create_total(self):
        self.pdf.set_y(self.pdf.get_y()+5)
        self.pdf.set_x(self.tableColumnDateWidth + self.tableColumnClientCodeWidth + self.tableColumnDescriptionWidth+10)
        self.pdf.set_font(family='Arial',style='B')
        self.pdf.cell(w=20, txt=f'Total',align='C')

        totalhours = 0
        for task in self.invoice.activity.tasks:
            totalhours += int(task.duration)
        
        self.pdf.set_x(self.pdf.get_x() + 5)
        self.pdf.cell(w=self.tableColumnHoursWidth, txt=f'{totalhours}')
        
        self.pdf.set_font(family='Arial')
    
    def create_seller_signature(self):
        current_y = self.pdf.get_y()
        self.pdf.set_xy(self.initialX + 30, self.pdf.get_y()+30)
        self.pdf.cell(w=20,txt=f'FURNIZOR: ', align = 'C')
        self.pdf.set_y(self.pdf.get_y() + 7)
        self.pdf.set_x(self.initialX + 30)
        self.pdf.cell(w=20,h=6,txt=f'{self.invoice.seller.name}',align = 'C', ln = 1)
        self.pdf.set_x(self.initialX + 30)
        self.pdf.cell(w=20,h=6,txt=f'Florinel',align = 'C', ln = 1)
        self.pdf.set_x(self.initialX + 30)
        self.pdf.cell(w=20,h=6,txt=f'L.S.',align = 'C', ln = 1)

        self.pdf.set_y(current_y)

    def create_buyer_signature(self):
        self.pdf.set_xy(self.initialX + 130, self.pdf.get_y()+30)
        self.pdf.cell(w=20,txt=f'BENEFICIAR: ', align = 'C')
        self.pdf.set_y(self.pdf.get_y() + 7)
        self.pdf.set_x(self.initialX + 130)
        self.pdf.cell(w=20,h=6,txt=f'{self.invoice.buyer.name}',align = 'C', ln = 1)
        self.pdf.set_x(self.initialX + 130)
        self.pdf.cell(w=20,h=6,txt=f'Mariusel',align = 'C', ln = 1)
        self.pdf.set_x(self.initialX + 130)
        self.pdf.cell(w=20,h=6,txt=f'L.S.',align = 'C', ln = 1)
        

    def writeToPage(self):
        self.pdf.output("demo_pdf.pdf")