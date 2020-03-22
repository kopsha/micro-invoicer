# micro-invoicer

Making invoices has never been easier

## Conceptualized API as use cases

1, load / create the registry

* `registry = install_registry(series, start_number, seller)`, or
* `registry = get_installed()`

2, load / create a contract

* `contract = registry.make_contract(buyer, hourly_rate)`, or
* `contract = registry.last_contract()`, or
* `contract = registry.find_contract(buyer)`

3, create new invoice

* `invoice = make_time_invoice(date, report, exchange_rate, contract)`, or
* `invoice = make_materials_invoice(date, price, quantity, contract)`

4, release all draft invoices

5, amend invoice (storno)


## Setup instructions

Before being able to generate (issue) a new invoice you need to provide some data to the script.
In the same folder, create the following json files and fill in your company and contract details as in the examples below:

`seller.json`
```json
{
    "name" : "AGRICULTORII VESELI S.R.L",
    "registration_id": "J12/3156/1010",
    "fiscal_code": "12345678",
    "address": "Castelul Fermecat, Comuna Imperiala, nr. 3, jud. Regatul Albastru",
    "bank_account": "RA12 TRRG RANC RT01 1234 5678",
    "bank_name": "Trezoreria Regala",
    "invoice_series" : "APR",
    "invoice_start_number" : 1
}
```

`contract.json`
```json
{
    "name" : "FAMILIA REGALA S.R.L.",
    "registration_id": "J12/0001/1001",
    "fiscal_code": "987654321",
    "address": "Castelul Regal, Orasul Minciunilor, nr. 1, jud. Regatul Albastru",
    "bank_account": "RA01 TRRG RANC RT01 0001 0001",
    "bank_name": "Trezoreria Regala",
    "hourly_rate" : 112
}
```


Then, run the script providing the json files created earlier as arguments:

```console
micro-invoicer $ python mini_invoicer.py --install seller.json --contract contract.json --commit
********************************************************************************
* Mini Invoicer                                                                *
********************************************************************************
All changes will be written to local database.
********************************************************************************
* Installing new invoice register                                              *
********************************************************************************
Created register for AGRICULTORII VESELI S.R.L
Created contract with FAMILIA REGALA S.R.L.
Local database updated successfully.
********************************************************************************
* AGRICULTORII VESELI S.R.L registry quick view                                *
********************************************************************************
Contracts:
  0 : FAMILIA REGALA S.R.L.
No invoices found in registry.
********************************************************************************
* [14:36:12] Finished in 0.00 seconds.                                         *
********************************************************************************
micro-invoicer $ _
```

Notice the `--commit` flag, which tells the script that you want to write the required changes to disk.

Now, the setup is complete so you can ...


### Issue a new invoice

In order to render (read as *issue*) a PDF with a new invoice, you need to provide the details of that invoice in a new json file.

`new_invoice.json`
```json
{
    "contract_id" : 0,
    "hours" : 128,
    "flavor": "authentication module",
    "project_id": "FooBar Banking",
    "xchg_rate" : 7.4551
}
```

Then, run the script with using the `--invoice` argument as below:
```console
micro-invoicer $ python mini_invoicer.py --invoice invoice.json --commit
********************************************************************************
* Mini Invoicer                                                                *
********************************************************************************
All changes will be written to local database.
********************************************************************************
* AGRICULTORII VESELI S.R.L registry quick view                                *
********************************************************************************
Contracts:
  0 : FAMILIA REGALA S.R.L.
No invoices found in registry.
New invoice:
   APR-0001 : FAMILIA REGALA S.R.L.            :     128 ore :   106876.31 lei
Local database updated successfully.
********************************************************************************
* [14:43:08] Finished in 0.01 seconds.                                         *
********************************************************************************
micro-invoicer $ _
```

And you're done.

For the next one, you only need to update this json file and run the script with `--invoice` argument again.


### Reqistry quick view

At some point, you may want to inspect the current registry and all you have to do is to run the script without arguments.

```console
micro-invoicer $ python mini_invoicer.py 
********************************************************************************
* Mini Invoicer                                                                *
********************************************************************************
Performing a dry run, local database will not be touched.
********************************************************************************
* AGRICULTORII VESELI S.R.L registry quick view                                *
********************************************************************************
Contracts:
  0 : FAMILIA REGALA S.R.L.
Last 5 invoices in registry:
   APR-0001 : FAMILIA REGALA S.R.L.            :     128 ore :   106876.31 lei
********************************************************************************
* [14:46:42] Finished in 0.00 seconds.                                         *
********************************************************************************
micro-invoicer $ _
```

You can see the full list of arguments with `--help`.

## Sitemap

 URL         | Title         | Template              | View Kind
 ----        | ----          | ----                  | ----
 /           | Home          | index.html            | registry quickview
 /profile    | Profile       | profile.html          | profile view (reset)
 /contract   | Contract      | contract.html         | contract detail view
 /contracts  | Contracts     | contract_list.html    | contract list view
 /invoice    | Invoice       | invoice.html          | invoice detail view
 /register/fiscal|           | fiscal_entity.html    | # will trigger reset

