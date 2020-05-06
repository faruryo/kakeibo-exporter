from datetime import date

import pytest

from kakeibo_exporter.domain.expense import Expenses
from kakeibo_exporter.repository.expense_db import ExpenseDb
from kakeibo_exporter.repository.expense_db_impl import ExpenseDbImpl
from tests.helpers import count_expenses_year


@pytest.fixture
def sqlite_db_path(tmpdir) -> str:
    tmpfile = tmpdir.join("test_db.sqlite3")

    yield str(tmpfile)


def test_super():
    """継承クラスチェック
    """
    assert ExpenseDb in ExpenseDbImpl.__bases__


def test_insert_clean(sqlite_db_path, expense_one, create_expenses_b2d):
    expenses = create_expenses_b2d(date(2016, 1, 1), date(2019, 12, 31))

    expense_db = ExpenseDbImpl("sqlite:///:memory:")

    assert expense_db.insert(expense_one) == 1
    assert expense_db.get() == expense_one

    expense_db.insert(expenses) == 1461
    assert expense_db.get() == expense_one + expenses

    expense_db.clean()
    assert expense_db.get() == Expenses([])

    # 上記のmemoryテストで十分そう
    expense_db = ExpenseDbImpl("sqlite:///" + sqlite_db_path)

    expense_db.insert(expense_one) == 1
    assert expense_db.get() == expense_one

    expense_db.insert(expense_one) == 1
    assert expense_db.get() == expense_one + expense_one

    expense_db.clean()
    assert expense_db.get() == Expenses([])


def test_delete_by_year(create_expenses_b2d):
    expense_db = ExpenseDbImpl("sqlite:///:memory:")

    expenses = create_expenses_b2d(date(2015, 1, 1), date(2018, 12, 31))

    expense_db.insert(expenses)
    assert expense_db.get() == expenses

    # 年ごと件数事前チェック
    before_expenses = expense_db.get()
    yc = count_expenses_year(before_expenses)
    assert yc == {2015: 365, 2016: 366, 2017: 365, 2018: 365}

    assert expense_db.delete_by_year(2016) == 366

    # 年ごと件数事前チェック
    deleted_expenses = expense_db.get()
    dyc = count_expenses_year(deleted_expenses)
    assert dyc == {2015: 365, 2017: 365, 2018: 365}
