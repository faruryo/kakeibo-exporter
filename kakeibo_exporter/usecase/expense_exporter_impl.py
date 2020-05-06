
from kakeibo_exporter.repository.expense_db import ExpenseDb
from kakeibo_exporter.repository.expense_sheet import ExpenseSheet
from kakeibo_exporter.usecase.expense_exporter import ExpenseExporter


class ExpenseExporterImpl(ExpenseExporter):
    def __init__(self, db: ExpenseDb, sheet: ExpenseSheet):
        self.db = db
        self.sheet = sheet

    def export_sheet2db(self, spreadsheetId: str) -> dict:
        expenses = self.sheet.get(spreadsheetId)
        ic = self.db.insert(expenses)

        return {
            "insert": ic
        }

    def sync_sheet2db(self, spreadsheetId: str) -> dict:
        expenses = self.sheet.get(spreadsheetId)
        ys = {e.date.year for e in expenses}
        dc = 0
        for y in ys:
            c = self.db.delete_by_year(y)
            dc = dc + c

        ic = self.db.insert(expenses)

        return {
            "insert": ic,
            "delete": dc
        }

    def clean_db(self):
        self.db.clean()
