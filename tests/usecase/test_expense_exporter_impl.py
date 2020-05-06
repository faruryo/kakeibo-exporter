from datetime import date

from kakeibo_exporter.repository.expense_db_impl import ExpenseDbImpl
from kakeibo_exporter.usecase.expense_exporter_impl import ExpenseExporterImpl
from tests.helpers import count_expenses_year


def test_export_sheet2db(mocker, expense_one):
    sheet_mock = mocker.Mock()
    sheet_mock.get.return_value = expense_one
    db = ExpenseDbImpl("sqlite:///:memory:")

    exporter = ExpenseExporterImpl(sheet=sheet_mock, db=db)

    assert exporter.export_sheet2db("") == {"insert": 1}

    assert expense_one == db.get()


def test_sync_sheet2db(mocker, create_expenses_b2d):
    expenses = create_expenses_b2d(date(2018, 1, 1), date(2020, 12, 31))

    sheet_mock = mocker.Mock()
    sheet_mock.get.return_value = expenses
    db = ExpenseDbImpl("sqlite:///:memory:")

    exporter = ExpenseExporterImpl(sheet=sheet_mock, db=db)

    # 二回実行しても同じ
    assert exporter.sync_sheet2db("") == {"insert": 1096, "delete": 0}
    assert db.get() == expenses

    assert exporter.sync_sheet2db("") == {"insert": 1096, "delete": 1096}
    assert db.get() == expenses
    assert count_expenses_year(db.get()) == {2018: 365, 2019: 365, 2020: 366}

    # 特定年だけsyncすると同じ年の他のデータは消えて、他の年のデータはそのまま
    expenses2019 = create_expenses_b2d(date(2019, 3, 1), date(2019, 3, 31))
    expenses2020 = create_expenses_b2d(date(2020, 1, 1), date(2020, 1, 31))
    sheet_mock.get.return_value = expenses2019 + expenses2020
    assert exporter.sync_sheet2db("") == {"insert": 62, "delete": 731}
    assert count_expenses_year(db.get()) == {2018: 365, 2019: 31, 2020: 31}


def test_clean_db(mocker):
    sheet_mock = mocker.Mock()
    db_mock = mocker.Mock()

    exporter = ExpenseExporterImpl(sheet=sheet_mock, db=db_mock)

    exporter.clean_db()

    db_mock.clean.assert_called()
