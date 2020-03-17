# mini-invoicer

Making invoices has never been easier

## use cases

* registry = install_registry(series, start_number, seller)
* registry = get_installed()

* contract = registry.make_contract(buyer, hourly_rate)
* contract = registry.last_contract()
* contract = registry.find_contract(buyer)

* activity = make_activity(contract, hours, project_code, flavor)
* report = list() of activities

* invoice = make_time_invoice(date, report, exchange_rate, contract)
* invoice = make_materials_invoice(date, price, quantity, contract)

* invoice.render_pdf(folder)

Setting up the program for demo

1. Create three files at the location of your python file (with your favorite editor) called:
	seller.json
	buyer.json
	invoice_data.json

MAKE SURE THE FILES ARE IN .json FORMAT.
DO NOT CREATE .txt FILES !


2. Copy and paste the following data (braces included):

-INTO FILE seller.json

{
    "name" : "AGRICULTORII VESELI S.R.L",
    "registration_id": "J12/3156/1010",
    "fiscal_code": "12345678",
    "address": "Castelul Fermecat, Comuna Imperiala, nr. 3 jud. Regatul Albastru",
    "bank_account": "RA12 TRRG RANC RT01 1234 5678",
    "bank_name": "Trezoreria Regala",
    "invoice_series" : "APR",
    "invoice_start_number" : 1
}



-INTO FILE buyer.json

{
    "name" : "FAMILIA REGALA S.R.L.",
    "registration_id": "J12/0001/1001",
    "fiscal_code": "987654321",
    "address": "Castelul Regal, Orasul Minunilor, nr. 1 jud. Regatul Albastru",
    "bank_account": "RA01 TRRG RANC RT01 0001 0001",
    "bank_name": "Trezoreria Regala",
    "hourly_rate" : 28
}


-INTO FILE invoice_data.json

{
    "contract_id" : 0,
    "hours" : 168,
    "flavor": "livrat",
    "project_id": "2.7_LVR_LEG",
    "xchg_rate" : 7.4551
}



3. Run the python file via command prompt / terminal with the required install arguments as shown IN THE FOLLOWING EXAMPLE 
python c:/Users/sergiu.adam/Documents/GitHub/micro-invoicer/mini_invoicer.py --install c:/Users/sergiu.adam/Documents/GitHub/micro-invoicer/seller.json -c c:/Users/sergiu.adam/Documents/GitHub/micro-invoicer/buyer.json --commit
Generalised as:
python "PATH_TO_MINI_INVOICER/"mini_invoicer.py --install "PATH_TO_MINI_INVOICER/"seller.json -c "PATH_TO_MINI_INVOICER/"buyer.json --commit
RUN THIS COMMAND ONLY ONCE, AT THE SETUP OF THE PROGRAM

In order to create a PDF invoice without saving the fact that a new invoice has been emitted, type
python "PATH_TO_MINI_INVOICER/"mini_invoicer.py -n "PATH_TO_MINI_INVOICER/"invoice_data.json

In order to create a PDF invoice WITH saving the fact that a new invoice has been emitted, type
python "PATH_TO_MINI_INVOICER/"mini_invoicer.py -n "PATH_TO_MINI_INVOICER/"invoice_data.json --commit


