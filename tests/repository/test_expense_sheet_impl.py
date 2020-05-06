from kakeibo_exporter.repository.expense_sheet import ExpenseSheet
from kakeibo_exporter.repository.expense_sheet_impl import ExpenseSheetImpl


def test_super():
    """継承クラスチェック
    """
    assert ExpenseSheet in ExpenseSheetImpl.__bases__


def test_get(mocker, expense_one):
    """driverからの入力とgetの出力のテスト
    """
    insmock = mocker.Mock()
    insmock.fetch_expenses.return_value = {
        "expenses": [
            {
                "date": expense.date,
                "category": expense.category,
                "debit": expense.debit,
                "credit": expense.credit,
                "price": expense.price,
                "remark": expense.remark,
            }
            for expense in expense_one
        ]
    }

    expense_sheet = ExpenseSheetImpl(sheet_driver=insmock)
    expenses = expense_sheet.get("spreadsheetid")

    assert expenses == expense_one
