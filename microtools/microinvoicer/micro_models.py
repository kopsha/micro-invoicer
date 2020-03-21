from dataclasses import dataclass, asdict, field
from datetime import datetime, date, timedelta
from typing import List
import enum
import json

@dataclass
class FiscalEntity:
    name: str
    owner_fullname: str
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


def fake_anonymous_data():
    seller = FiscalEntity(**{
                "name": "Anonymous",
                "owner_fullname": "Giani Uragan",
                "registration_id": "J26/377/2007",
                "fiscal_code": "21236676",
                "address": "Calatele village, No. 185",
                "bank_account": "RA01 TRRG RANC RT01 0001 0001",
                "bank_name": "Trezoreria Regala"
            })
    register = InvoiceRegister(**{
            "seller": seller,
            "invoice_series": "AAA",
            "next_number": 11,
            "invoices": [{
                'series_number' : 'AAA-0001',
                'buyer' : 'ANONYMOUS S.R.L.',
                'duration' : 128,
                'value' : 106876.31,
            },
            {
                'series_number' : 'AAA-0002',
                'buyer' : 'ANONYMOUS S.R.L.',
                'duration' : 92,
                'value' : 6995.12,
            }]
        })
    db = LocalStorage(register=register)
    return db
