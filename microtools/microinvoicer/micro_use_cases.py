import enum
import json
import random
import decimal
import zlib

from dataclasses import dataclass, asdict, field
from datetime import datetime, date, timedelta
from typing import List

from .micro_models import *
from . import micro_render


def previous_month():
    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month = last_month.replace(day=1)
    return last_month


def corrupted_storage():
    form_data = {
        'invoice_series': '(corrupted)',
        'start_no': 1,
        'name': 'Account corrupted. Please reset your profile.',
        'owner_fullname': '(corrupted)',
        'registration_id': '(corrupted)',
        'fiscal_code': '(corrupted)',
        'address': '(corrupted)',
        'bank_account': '(corrupted)',
        'bank_name': '(corrupted)',
    }
    return create_empty_db(form_data)


def create_empty_db(form_data):
    invoice_series = form_data.pop('invoice_series')
    start_no = form_data.pop('start_no')

    seller = FiscalEntity(**form_data)
    registry = InvoiceRegister(seller=seller, invoice_series=invoice_series, next_number=start_no)
    db = LocalStorage(registry)

    return db


def create_contract(form_data):
    hourly_rate = form_data.pop('hourly_rate')
    registry_id = form_data.pop('registry_id')
    registry_date = form_data.pop('registry_date')
    buyer = FiscalEntity(**form_data)
    contract = ServiceContract(
        buyer=buyer,
        registry_id=registry_id,
        registry_date=registry_date,
        hourly_rate=hourly_rate
    )

    return contract


def create_time_invoice(db, form_data):
    contract_id = form_data.pop('contract_id')
    duration = form_data.pop('duration')
    flavor = form_data.pop('flavor')
    project_id = form_data.pop('project_id')

    contract = db.contracts[int(contract_id)]
    invoice_fields = {
        'status': InvoiceStatus.DRAFT,
        'seller': db.register.seller,
        'series': db.register.invoice_series,
        'number': db.register.next_number,
        'buyer': contract.buyer,
        'hourly_rate': contract.hourly_rate,
        'activity': create_random_activity(contract_id, duration, flavor, project_id),
        'conversion_rate': form_data.pop('xchg_rate'),
        'publish_date': form_data.pop('publish_date'),
        'contract_registry_id': contract.registry_id,
        'contract_registry_date': contract.registry_date,
    }
    return TimeInvoice(**invoice_fields)


def draft_time_invoice(db, form_data):
    invoice = create_time_invoice(db, form_data)
    db.register.next_number += 1
    db.register.invoices.append(invoice)

    return db


def discard_last_invoice(db):
    discared_invoice = db.register.invoices.pop()
    db.register.next_number -= 1
    # TODO: this object could be added to a trash bin
    return db


def render_printable_invoice(invoice):
    assert type(invoice) is TimeInvoice
    return micro_render.write_invoice_pdf(invoice)


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
        left -= current_split

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


def create_random_tasks(activity, how_many, hours):

    names = pick_task_names(flavor=activity.flavor, count=how_many)
    durations = split_duration(duration=hours, count=how_many)
    dates = compute_start_dates(activity.start_date, durations)
    projects = [activity.project_id] * how_many

    tasks = [Task(*t) for t in zip(names, dates, durations, projects)]

    return tasks


def create_random_activity(contract_id, hours, flavor, project_id):
    start_date = previous_month()
    activity = ActivityReport(contract_id, start_date, flavor, project_id)
    how_many = random.randrange(8, stop=13)
    activity.tasks = create_random_tasks(activity, how_many, hours=hours)

    return activity


def loads(content):
    def from_dict(pairs):
        factory_map = {
            'seller': FiscalEntity,
            'buyer': FiscalEntity,
            'register': InvoiceRegister,
            'activity': ActivityReport,
            'contracts': ServiceContract,
            'tasks': Task,
            'invoices': TimeInvoice,
        }
        # ATTENTION: if you rename any fields check this part too
        date_fields = [
            'start_date',
            'date',
            'registry_date',
            'publish_date',
            'contract_registry_date',
        ]
        obj = {}

        for key, value in pairs:
            if key in factory_map:
                if isinstance(value, list):
                    obj[key] = [factory_map[key](**item) for item in value]
                else:
                    obj[key] = factory_map[key](**value)
            elif key in date_fields:
                obj[key] = date.fromisoformat(value)
            else:
                obj[key] = value

        return obj

    data = json.loads(content, object_pairs_hook=from_dict)

    return LocalStorage(register=data['register'], contracts=data['contracts'])


def dumps(db):
    def custom_serializer(obj):
        if isinstance(obj, date):
            return obj.isoformat()

        if isinstance(obj, decimal.Decimal):
            return float(obj)

        raise TypeError(f'Type {type(obj)} is not JSON serializable')

    content = json.dumps(asdict(db), indent=4, default=custom_serializer)
    return content


def to_crc32(data):
    return hex(zlib.crc32(data.encode('utf-8')) & 0xffffffff)


if __name__ == '__main__':
    print('This is a pure module, it cannot be executed.')
