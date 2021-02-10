from dataclasses import dataclass, asdict, field
from datetime import datetime, date, timedelta
from typing import List
import enum
import inspect
import json
import sys


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
    registry_id: str
    registry_date: date


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
    publish_date: date
    contract_registry_id: str
    contract_registry_date: date

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

    def flatten_contracts(self):
        return [asdict(c) for c in self.contracts]

    def invoices(self):
        return list(reversed(self.register.invoices))
