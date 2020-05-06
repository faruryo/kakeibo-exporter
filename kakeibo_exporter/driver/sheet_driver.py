from abc import ABCMeta, abstractmethod


class SheetDriver(metaclass=ABCMeta):
    @abstractmethod
    def fetch_expenses(self, spreadsheetId: str) -> dict:
        raise NotImplementedError
