import pytest
from fastapi.testclient import TestClient

from kakeibo_exporter.api.app import ExpenseExporterFactory
from kakeibo_exporter.api.app import app as api_app
from kakeibo_exporter.api.app import exporter as exporter_factory

client = TestClient(api_app)


def test_ExpenseExporterFactory_no_set(mocker):
    """ExpenseExporterFactoryの仕様チェック
        setを使用せずにcallした場合にExceptionが出る
    """
    factory = ExpenseExporterFactory()

    with pytest.raises(Exception):
        factory()


def test_ExpenseExporterFactory_return_exporter(mocker):
    """ExpenseExporterFactoryの仕様チェック
        callされたときにセットしたオブジェクトが返る
    """

    exporter_mock = mocker.Mock()

    factory = ExpenseExporterFactory()

    factory.set(exporter_mock)

    assert factory() == exporter_mock


def test_sync_expense_success(mocker):
    """成功時の仕様チェック
        200エラーとその内容を返す
    """
    exporter_mock = mocker.Mock()
    exporter_mock.sync_sheet2db.return_value = {"insert": 3, "delete": 0}

    exporter_factory.set(exporter_mock)
    response = client.get("/expense/sync/test_spreadsheet_id",)
    assert response.status_code == 200
    assert response.json() == {"insert": 3, "delete": 0}


def test_sync_expense_error(mocker):
    """内部エラー時の仕様チェック
        500エラーとその内容を返す
    """
    exporter_mock = mocker.Mock()
    exporter_mock.sync_sheet2db.side_effect = Exception("不明なエラーが発生しています。")

    exporter_factory.set(exporter_mock)
    response = client.get("/expense/sync/test_spreadsheet_id",)
    assert response.status_code == 500
    assert response.json() == {"detail": "不明なエラーが発生しています。"}
