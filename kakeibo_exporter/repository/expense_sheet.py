from abc import ABCMeta, abstractmethod

from kakeibo_exporter.domain.expense import Expenses


class ExpenseSheet(metaclass=ABCMeta):
    @abstractmethod
    def get(self, spreadsheetId: str) -> Expenses:
        raise NotImplementedError
