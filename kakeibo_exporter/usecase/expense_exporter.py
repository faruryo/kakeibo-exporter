from abc import ABCMeta, abstractmethod


class ExpenseExporter(metaclass=ABCMeta):
    @abstractmethod
    def export_sheet2db(self, spreadsheetId: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def sync_sheet2db(self, spreadsheetId: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def clean_db(self):
        raise NotImplementedError
