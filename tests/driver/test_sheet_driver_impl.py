import json
from datetime import date

import googleapiclient
import httplib2
import pytest
from googleapiclient.http import RequestMockBuilder

from kakeibo_exporter.driver.sheet_driver import SheetDriver
from kakeibo_exporter.driver.sheet_driver_impl import SheetDriverImpl


@pytest.fixture
def driver() -> SheetDriverImpl:
    return SheetDriverImpl()


def test_super():
    """継承クラスチェック
    """
    assert SheetDriver in SheetDriverImpl.__bases__


# TODO:テストが遅いので改善が必要
def test_fetch_expenses(mocker):
    # RequestMockBuilderがMockなのに認証情報が必要になっているので回避するためのもの
    # 使い方が間違ってるのか？
    mocker.patch("google.auth.default", return_value=(None, None))
    # driver用
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("os.path.open")
    mocker.patch("pickle.dump")
    mocker.patch("pickle.load")
    batchGet_response = json.dumps(
        {
            "spreadsheetId": "106NrG6bOe3Hh3wx5iNo0_XdQ0sZuKYlJaStOHuNavAg",
            "valueRanges": [
                {
                    "range": "'1月'!A2:F1000",
                    "majorDimension": "ROWS",
                    "values": [
                        [42370, "家賃", "家賃", 200000, "共用銀行口座"],
                        [42383, "住居費", "電気代", 30000, "共用銀行口座"],
                    ],
                },
                {
                    "range": "'2月'!A2:F1000",
                    "majorDimension": "ROWS",
                    "values": [
                        [42401, "家賃", "家賃", 200000, "共用銀行口座"],
                        ["", "住居費", "電気代", 30000, "共用銀行口座"],
                    ],
                },
            ],
        }
    )
    get_response = json.dumps(
        {
            "spreadsheetId": "106NrG6bOe3Hh3wx5iNo0_XdQ0sZuKYlJaStOHuNavAg",
            "properties": {"title": "【公開】2016家計簿サンプル"},
            "sheets": [
                {"properties": {"title": "1月"}},
                {"properties": {"title": "2月"}},
            ],
        }
    )

    requestBuilder = RequestMockBuilder(
        {
            "sheets.spreadsheets.values.batchGet": (None, batchGet_response),
            "sheets.spreadsheets.get": (None, get_response),
        },
        check_unexpected=True,
    )
    service = googleapiclient.discovery.build(
        "sheets", "v4", requestBuilder=requestBuilder
    )
    driver = SheetDriverImpl()
    driver.spreadsheets = service.spreadsheets()

    assert driver.fetch_expenses("106NrG6bOe3Hh3wx5iNo0_XdQ0sZuKYlJaStOHuNavAg") == {
        "expenses": [
            {
                "date": date(2016, 1, 1),
                "category": "家賃",
                "debit": "家賃",
                "credit": "共用銀行口座",
                "price": 200000,
                "remark": "",
            },
            {
                "date": date(2016, 1, 14),
                "category": "住居費",
                "debit": "電気代",
                "credit": "共用銀行口座",
                "price": 30000,
                "remark": "",
            },
            {
                "date": date(2016, 2, 1),
                "category": "家賃",
                "debit": "家賃",
                "credit": "共用銀行口座",
                "price": 200000,
                "remark": "",
            },
            {
                "date": date(2016, 2, 1),
                "category": "住居費",
                "debit": "電気代",
                "credit": "共用銀行口座",
                "price": 30000,
                "remark": "",
            },
        ]
    }


def test_fetch_expenses_spreadsheetid_not_exists(mocker):
    # RequestMockBuilderがMockなのに認証情報が必要になっているので回避するためのもの
    # 使い方が間違ってるのか？
    mocker.patch("google.auth.default", return_value=(None, None))
    # driver用
    mocker.patch("google.oauth2.service_account.Credentials.from_service_account_file")
    mocker.patch("os.path.open")
    mocker.patch("pickle.dump")
    mocker.patch("pickle.load")

    requestBuilder = RequestMockBuilder(
        {
            "sheets.spreadsheets.get": (
                httplib2.Response(
                    {"status": 404, "reason": "Requested entity was not found."}
                ),
                b"{}",
            )
        },
        check_unexpected=True,
    )
    service = googleapiclient.discovery.build(
        "sheets", "v4", requestBuilder=requestBuilder
    )
    driver = SheetDriverImpl()
    driver.spreadsheets = service.spreadsheets()

    with pytest.raises(Exception):
        driver.fetch_expenses("1234")
