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
