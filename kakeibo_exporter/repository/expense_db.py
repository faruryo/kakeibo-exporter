from abc import ABCMeta, abstractmethod

from kakeibo_exporter.domain.expense import Expenses


class ExpenseDb(metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> Expenses:
        raise NotImplementedError

    @abstractmethod
    def insert(self, expenses: Expenses) -> int:
        raise NotImplementedError

    @abstractmethod
    def clean(self):
        raise NotImplementedError

    @abstractmethod
    def delete_by_year(self, year: int) -> int:
        raise NotImplementedError
