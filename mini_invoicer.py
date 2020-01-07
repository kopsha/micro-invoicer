import argparse
import json
import os
import timeit
import humanize

from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List
from contextlib import suppress

def print_stage(text, row_size=80):
    """Pretty banner stage printing helper"""
    filler=' '*(row_size-4-len(text))
    print(f"{'*'*row_size}");
    print(f"* {text}{filler} *")
    print(f"{'*'*row_size}");

@dataclass
class FiscalEntity:
    name: str
    registration_id: str
    fiscal_code: str
    address: str
    bank_account: str
    bank_name: str

@dataclass
class InvoiceRegister:
    seller: FiscalEntity
    invoice_series: str
    next_number: int

@dataclass
class ServiceContract:
    buyer: FiscalEntity
    hourly_rate: float

@dataclass
class LocalStorage:
    register: InvoiceRegister
    contracts: List[ServiceContract] = field(default_factory=list)

def clean_data_files():
    known_data_files = [
        'active_registry.json',
        'local_database.json'
    ]

    for fname in known_data_files:
        with suppress(OSError):
            os.remove(fname)
            print(f'Deleted {fname}')

def install_registry(install_json):
    if not os.path.isfile(install_json):
        raise ValueError(f'The provided path {install_json} is not a valid file.')

    with open(install_json) as file:
        data = json.loads(file.read())

    _, start_no = data.popitem()
    _, series = data.popitem()
    seller = FiscalEntity(**data)
    
    registry = InvoiceRegister(seller=seller, invoice_series=series, next_number=start_no)
    print_stage(f'Creating {registry.seller.name} registry')

    clean_data_files()
    with open('active_registry.json', 'wt') as file:
        file.write(json.dumps(asdict(registry), indent=4))

    return registry

def register_contract(contract_json):
    if not os.path.isfile(contract_json):
        raise ValueError(f'The provided path {contract_json} is not a valid file.')

    with open(contract_json) as file:
        data = json.loads(file.read())

    _, hourly_rate = data.popitem()
    buyer = FiscalEntity(**data)
    contract = ServiceContract(buyer=buyer, hourly_rate=hourly_rate)
    print(f'Created contract with {buyer.name}')

    return contract

def load_database():
    if not os.path.isfile('local_database.json'):
        return None

    with open('local_database.json') as file:
        data = json.loads(file.read())

    db = LocalStorage(
        register=data['register'],
        contracts=data['contracts'],
    )

    return db

def save_database(db):
    with open('local_database.json', 'wt') as file:
        file.write(json.dumps(asdict(db), indent=4))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--install', help='setup a new local registry using provided json as seller')
    parser.add_argument('-c', '--contract', help='create a new contract using provided json as buyer')
    parser.add_argument('-q', '--quickie', help='create a new time invoice based on last one')
    args = parser.parse_args()

    if (args.install):
        if not args.contract:
            parser.error('Installation requires a contract too.')

        registry = install_registry(args.install)
        contract = register_contract(args.contract)
        db = LocalStorage(registry, contract)
        save_database(db)

    db = load_database()
    if not db:
        print('Local database was not found, please run setup first.')
        return


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
