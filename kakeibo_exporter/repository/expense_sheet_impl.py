from kakeibo_exporter.domain.expense import Expense, Expenses
from kakeibo_exporter.driver.sheet_driver import SheetDriver
from kakeibo_exporter.repository.expense_sheet import ExpenseSheet


class ExpenseSheetImpl(ExpenseSheet):
    sheet_driver: SheetDriver

    def __init__(self, sheet_driver: SheetDriver):
        self.sheet_driver = sheet_driver

    def get(self, spreadsheetId: str) -> Expenses:
        res = self.sheet_driver.fetch_expenses(spreadsheetId)
        return Expenses(
            values=[
                Expense(
                    date=a["date"],
                    category=a["category"],
                    debit=a["debit"],
                    credit=a["credit"],
                    price=a["price"],
                    remark=a["remark"],
                )
                for a in res["expenses"]
            ]
        )
