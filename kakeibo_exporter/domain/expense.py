from dataclasses import dataclass
from datetime import date

from kakeibo_exporter.domain.collection import Collection


@dataclass(frozen=True)
class Expense:
    date: date
    category: str
    debit: str
    credit: str
    price: int
    remark: str


@dataclass(frozen=True)
class Expenses(Collection[Expense]):
    values: [Expense]
