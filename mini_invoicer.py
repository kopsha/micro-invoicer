import argparse
import json
import os
import timeit
import humanize

from datetime import datetime
from dataclasses import dataclass, asdict

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
class MiniRegistry:
    seller: FiscalEntity
    invoice_series: str
    next_number: int

def install_registry(install_json):
    if not os.path.isfile(install_json):
        raise ValueError(f'The provided path {install_json} is not a valid file.')

    with open(install_json, "rt") as file:
        data = json.loads( file.read() )

    _, start_no = data.popitem()
    _, series = data.popitem()
    seller = FiscalEntity(**data)
    
    registry = MiniRegistry(seller=seller, invoice_series=series, next_number=start_no)
    print_stage(f'Creating {registry.seller.name} registry')

    with open("active_registry.json", "wt") as file:
        file.write(json.dumps(asdict(registry), indent=4))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--install', help='setup a new local registry using provided json as seller')
    args = parser.parse_args()

    if (args.install):
        install_registry(args.install)
        

if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
