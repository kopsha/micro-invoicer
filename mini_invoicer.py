import argparse
import json
import os
import timeit
import random

from datetime import datetime, date, timedelta
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
class Task:
    name: str
    date: datetime
    duration: float
    project_id: str

@dataclass
class ActivityReport:
    contract_id: int
    start_date: datetime
    hours: float
    flavor: str
    project_id: str
    tasks: List[Task] = field(default_factory=list)

@dataclass
class LocalStorage:
    register: InvoiceRegister
    contracts: List[ServiceContract] = field(default_factory=list)

def previous_month():
    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month = last_month.replace(day=1)    
    return last_month

def make_registry(install_json):
    if not os.path.isfile(install_json):
        raise ValueError(f'The provided path {install_json} is not a valid file.')

    with open(install_json) as file:
        data = json.loads(file.read())

    _, start_no = data.popitem()
    _, series = data.popitem()
    seller = FiscalEntity(**data)
    registry = InvoiceRegister(seller=seller, invoice_series=series, next_number=start_no)
    print(f'Created register for {seller.name}')

    return registry

def make_contract(contract_json):
    if not os.path.isfile(contract_json):
        raise ValueError(f'The provided path {contract_json} is not a valid file.')

    with open(contract_json) as file:
        data = json.loads(file.read())

    _, hourly_rate = data.popitem()
    buyer = FiscalEntity(**data)
    contract = ServiceContract(buyer=buyer, hourly_rate=hourly_rate)
    print(f'Created contract with {buyer.name}')

    return contract

def pick_task_names(flavor, count):
    taskname_pool = [
        "sprint planning"
        "sprint review",
        "development tasks estimation"
        "defects investigation",
        "code reviews",
        "refactoring old-code",
        "SDK architecture updates",
        "release notes"
        "{flavor} generic mock setup",
        "{flavor} state manager",
        "{flavor} components architecture",
        "{flavor} android communication layer",
        "{flavor} android native implementation",
        "{flavor} iOs communication layer",
        "{flavor} iOs native implementation",
        "{flavor} core implementation",
        "{flavor} public interfaces update",
        "{flavor} sample application",
        "{flavor} component design",
        "{flavor} data modeling",
        "{flavor} defects verification",
        "{flavor} code coverage testing"
        "Low level {flavor} event handling",
    ]
    tasks = [name.format(flavor=flavor) for name in random.sample(taskname_pool, k=count)]
    return tasks

def split_duration(duration, count):
    left = duration
    splits = []
    step = 1

    for step in range(count-1):
        max_split = round(left*(0.618*(step+2)/count))
        min_split = min(4, max_split-1)
        current_split = random.randrange(min_split, stop=max_split)
        splits.append(current_split)
        left -=current_split

    splits.append(left)

    return splits

def compute_start_dates(start_date, durations):
    dates = []
    trace_date = start_date
    for duration in durations:
        trace_date += timedelta(days=round(duration/8))
        if trace_date.weekday() > 4:
            trace_date += timedelta(days=7 - trace_date.weekday())
        dates.append(trace_date)

    return dates

def make_random_tasks(activity, how_many):
    
    names = pick_task_names(flavor=activity.flavor, count=how_many)
    durations = split_duration(duration=activity.hours, count=how_many)
    dates = compute_start_dates(activity.start_date, durations)
    projects = [activity.project_id] * how_many

    tasks = [Task(*t) for t in zip(names, dates, durations, projects)]

    return tasks

def make_random_activity(contract_id, hours, flavor, project_id):
    start_date = previous_month()
    activity = ActivityReport(contract_id, start_date, hours, flavor, project_id)
    how_many = random.randrange(8, stop=13)
    activity.tasks = make_random_tasks(activity, how_many)

    return activity

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

def clean_data_files():
    known_data_files = [
        'active_registry.json',
        'local_database.json'
    ]

    for fname in known_data_files:
        with suppress(OSError):
            os.remove(fname)
            print(f'Deleted {fname}')

def setup(seller_json, buyer_json):
    print_stage(f'Installing new invoice register')
    clean_data_files()
    registry = make_registry(seller_json)
    contract = make_contract(buyer_json)
    db = LocalStorage(registry, contract)
    save_database(db)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--install', help='setup a new local registry using provided json as seller')
    parser.add_argument('-c', '--contract', help='create a new contract using provided json as buyer')
    parser.add_argument('-q', '--quickie', help='create a new time invoice based on last one')
    args = parser.parse_args()

    if (args.install):
        if not args.contract:
            parser.error('Installation requires a contract too.')
        setup(args.install, args.contract)

    db = load_database()
    if not db:
        print('Local database was not found, please run setup first.')
        return

    a = make_random_activity(9, 120, 'aroma', '2.5')
    print(a)

if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
