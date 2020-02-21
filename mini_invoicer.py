import argparse
import enum
import json
import os
import random
import pdf_rendering as pdf
import timeit


from contextlib import suppress
from dataclasses import dataclass, asdict, field
from datetime import datetime, date, timedelta
from typing import List


def print_stage(text, row_size=80):
    """Pretty banner stage printing helper"""
    filler=' '*(row_size-4-len(text))
    print(f"{'*'*row_size}")
    print(f"* {text}{filler} *")
    print(f"{'*'*row_size}")


@dataclass
class FiscalEntity:
    name: str
    registration_id: str
    fiscal_code: str
    address: str
    bank_account: str
    bank_name: str


@dataclass
class ServiceContract:
    buyer: FiscalEntity
    hourly_rate: float


@dataclass
class Task:
    name: str
    date: date
    duration: float
    project_id: str


@dataclass
class ActivityReport:
    contract_id: int
    start_date: date
    flavor: str
    project_id: str
    tasks: List[Task] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return sum(t.duration for t in self.tasks)


@enum.unique
class InvoiceStatus(enum.IntEnum):
    DRAFT = enum.auto()
    PUBLISHED = enum.auto()
    STORNO = enum.auto()


@dataclass
class TimeInvoice:
    seller: FiscalEntity
    buyer: FiscalEntity
    activity: ActivityReport
    series: str
    number: int
    status: InvoiceStatus
    conversion_rate: float
    hourly_rate: float

    @property
    def series_number(self):
        return f'{self.series}-{self.number:04}'

    @property
    def unit_price(self):
        return self.conversion_rate * self.hourly_rate

    @property
    def value(self):
        return self.unit_price * self.activity.duration

    def __repr__(self):
        return f'{self.series_number:>11} : {self.buyer.name:32} : {self.activity.duration:7.0f} ore : {self.value:11.02f} lei'


@dataclass
class InvoiceRegister:
    seller: FiscalEntity
    invoice_series: str
    next_number: int
    invoices: List[TimeInvoice] = field(default_factory=list)

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
    print(install_json)
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
        "sprint planning",
        "sprint review",
        "development tasks estimation",
        "defects investigation",
        "code reviews",
        "refactoring old-code",
        "SDK architecture updates",
        "release notes",
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
        "{flavor} code coverage testing",
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

def make_random_tasks(activity, how_many, hours):
    
    names = pick_task_names(flavor=activity.flavor, count=how_many)
    durations = split_duration(duration=hours, count=how_many)
    dates = compute_start_dates(activity.start_date, durations)
    projects = [activity.project_id] * how_many

    tasks = [Task(*t) for t in zip(names, dates, durations, projects)]

    return tasks

def make_random_activity(contract_id, hours, flavor, project_id):
    start_date = previous_month()
    activity = ActivityReport(contract_id, start_date, flavor, project_id)
    how_many = random.randrange(8, stop=13)
    activity.tasks = make_random_tasks(activity, how_many, hours=hours)

    return activity


def make_time_invoice(db, contract_id, hours, flavor, project_id, xchg_rate):
    contract = db.contracts[contract_id]
    invoice_fields = {
        'status': InvoiceStatus.DRAFT,
        'seller': db.register.seller,
        'series': db.register.invoice_series,
        'number': db.register.next_number,
        'buyer': contract.buyer,
        'hourly_rate': contract.hourly_rate,
        'activity': make_random_activity(contract_id, hours, flavor, project_id),
        'conversion_rate': xchg_rate,
    }
    return TimeInvoice(**invoice_fields)

def issue_draft_invoice(db, invoice):
    if invoice.status != InvoiceStatus.DRAFT:
        raise ValueError(f'Only invoices with {InvoiceStatus.DRAFT!r} status can be registered, got {invoice.status!r}.')

    db.register.next_number += 1
    invoice.status = InvoiceStatus.PUBLISHED
    db.register.invoices.append(invoice)
    pdf.render_activity_report(invoice)
    pdf.render_invoice(invoice)

def cls_from_dict(pairs):
    obj = {k:v for k,v in pairs}

    if 'seller' in obj:
        obj['seller'] = FiscalEntity(**obj['seller'])

    if 'buyer' in obj:
        obj['buyer'] = FiscalEntity(**obj['buyer'])

    if 'register' in obj:
        obj['register'] = InvoiceRegister(**obj['register'])

    if 'contracts' in obj:
        obj['contracts'] = [ServiceContract(**contract_obj) for contract_obj in obj['contracts']]

    if 'tasks' in obj:
        obj['tasks'] = [Task(**task_obj) for task_obj in obj['tasks']]

    if 'activity' in obj:
        obj['activity'] = ActivityReport(**obj['activity'])

    if 'invoices' in obj:
        obj['invoices'] = [TimeInvoice(**invoice_obj) for invoice_obj in obj['invoices']]

    return obj


def load_database():
    if not os.path.isfile('local_database.json'):
        return None

    with open('local_database.json') as file:
        data = json.loads(file.read(), object_pairs_hook=cls_from_dict)

    db = LocalStorage(
        register=data['register'],
        contracts=data['contracts'],
    )

    return db

def save_database(db, commit_changes):
    def date_serializer(obj):
        if isinstance(obj, date):
            return obj.isoformat()

        raise TypeError(f'Type {type(obj)} is not JSON serializable')

    if commit_changes:
        with open('local_database.json', 'wt') as file:
            file.write(json.dumps(asdict(db), indent=4, default=date_serializer))
            print('Local database updated successfully.')
    else:
        dummy_buffer = json.dumps(asdict(db), indent=4, default=date_serializer)
        print(f'Skipped writing {len(dummy_buffer)} bytes to local database.')


def clean_data_files(commit_changes):
    known_data_files = [
        'active_registry.json',
        'local_database.json'
    ]

    for fname in known_data_files:
        with suppress(OSError):
            if commit_changes:
                os.remove(fname)
                print(f'Deleted {fname}')
            else:
                print(f'Should delete {fname}')


def setup(seller_json, buyer_json, commit_changes):
    print_stage(f'Installing new invoice register')

    clean_data_files(commit_changes)

    registry = make_registry(seller_json)
    contract = make_contract(buyer_json)
    db = LocalStorage(registry)
    db.contracts.append(contract)

    save_database(db, commit_changes)


def main():
    print_stage('Mini Invoicer')
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true', help='write changes to the db, without this it will print only')
    parser.add_argument('-i', '--install', help='setup a new local registry using provided json as seller')
    parser.add_argument('-c', '--contract', help='create a new contract using provided json as buyer')
    parser.add_argument('-q', '--quickie', help='issue a new time invoice based on last one')
    parser.add_argument('-n', '--invoice', help='issue a new time invoice using json file')
    args = parser.parse_args()

    if args.commit:
        print('All changes will be written to local database.')
    else:
        print('Performing a dry run, local database will not be touched.')

    if (args.install):
        if not args.contract:
            parser.error('Installation requires a contract too.')
        setup(args.install, args.contract, args.commit)

    db = load_database()
    if not db:
        print('Local database was not found, please run with --install first.')
        return

    print_stage(f'{db.register.seller.name} registry quick view')
    print('Contracts:')
    for i, c in enumerate(db.contracts):
        print(f'{i:>3} : {c.buyer.name}')
    if db.register.invoices:
        print('Last 5 invoices in registry:')
        for i in db.register.invoices[-5:]:
            print(i)
    else:
        print('No invoices found in registry.')

    if args.invoice:
        if not os.path.isfile(args.invoice):
            print(f'Error: Provided invoice data is not a file.')

        with open(args.invoice) as file:
            data = json.loads(file.read())

        invoice = make_time_invoice(db, **data)
        issue_draft_invoice(db, invoice)
        print(f'New invoice:\n{invoice!r}')
        save_database(db, args.commit)

if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
