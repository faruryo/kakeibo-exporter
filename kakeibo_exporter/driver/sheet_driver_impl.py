import os.path
import pickle
import re
from datetime import date, timedelta
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource, build

from kakeibo_exporter.driver.sheet_driver import SheetDriver

RANGE_NAME = "A2:F"


class SheetDriverImpl(SheetDriver):
    spreadsheets: Resource

    def __init__(self):

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # TODO: 認証情報の保存場所の調整が必要
        #       ライブラリ利用時、CLI利用時などを考えるとコンストラクタ引数でもらうのが良いか？
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = Credentials.from_service_account_file("credentials.json")
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        self.spreadsheets = service.spreadsheets()

    def _fetch_expense_sheets(self, spreadsheetId: str) -> list:
        """スプレッドシートに存在する支出シートをすべて取得する

        Arguments:
            spreadsheetId {str} -- 取得する支出シートのスプレッドシートID

        Returns:
            list -- 支出シート情報
        """

        try:
            result = self.spreadsheets.get(spreadsheetId=spreadsheetId).execute()
        except Exception:
            raise Exception(f"{spreadsheetId}が存在しない。")

        ss_title = result["properties"]["title"]
        y_p = re.compile("20[1-2][0-9]")
        year = y_p.search(ss_title).group()

        m_p = re.compile("([1-9]|1[0-2])月")
        exp_sheets = []
        for d in result.get("sheets", []):
            m = m_p.match(d["properties"]["title"])
            if m:
                exp_sheets.append(
                    {
                        "title": d["properties"]["title"],
                        "year": int(year),
                        "month": int(m.group(1)),
                    }
                )

        return exp_sheets

    def _get_sheet_title_by_A1(self, a1: str) -> str:
        """A1 notationからシート名のみを抜き出して返す

        Arguments:
            a1 {str} -- A1 notationの文字列

        Returns:
            str -- シート名
        """

        a_p = re.compile("'(.+)'![A-Z]+[0-9]+:[A-Z]+[0-9]+")
        sheet_title = a_p.search(a1).group(1)

        return sheet_title

    def _excel_date(self, xldate: int) -> date:
        """エクセルシリアル形式の日付をdate型に変換する

        Arguments:
            xldate {int} -- エクセルシリアル形式の日付

        Returns:
            date -- date
        """

        return date(1899, 12, 30) + timedelta(days=xldate)

    def _format_expenses_date(self, sheets: list, expenses: list) -> list:
        """支出情報の未記載日付を整形する

        Arguments:
            sheets {list} -- シート情報
            expenses {list} -- 支出情報

        Returns:
            list -- [description]
        """

        cp_expenses = []

        default_date_by_sheet_title = {
            sheet["title"]: date(sheet["year"], sheet["month"], 1) for sheet in sheets
        }

        for valueRange in expenses:
            title = self._get_sheet_title_by_A1(valueRange["range"])
            default_date = default_date_by_sheet_title[title]
            for values in valueRange["values"]:
                cp_expenses.append(
                    {
                        "date": self._excel_date(int(values[0]))
                        if values[0] != ""
                        else default_date,
                        "category": values[1],
                        "debit": values[2],
                        "credit": values[4],
                        "price": int(values[3]) if values[3] != "" else 0,
                        "remark": values[5] if len(values) > 5 else "",
                    }
                )

        return cp_expenses

    def _batch_get(self, spreadsheetId: str, range_names: List[str]) -> dict:
        """スプレッドシートから複数範囲指定されたデータを取得する

        Arguments:
            spreadsheetId {str} -- 取得する対象のスプレッドシートID
            range_names {List[str]} -- 取得する範囲(A1表記)のリスト

        Returns:
            dict -- 問合せ結果データ
        """

        request = self.spreadsheets.values().batchGet(
            spreadsheetId=spreadsheetId,
            ranges=range_names,
            valueRenderOption="UNFORMATTED_VALUE",
            dateTimeRenderOption="SERIAL_NUMBER",
        )
        result = request.execute()

        return result

    def fetch_expenses(self, spreadsheetId: str) -> dict:
        """スプレッドシートに存在する支出情報をすべて取得する

        Arguments:
            spreadsheetId {str} -- 取得する対象のスプレッドシートID

        Returns:
            dict -- 支出情報
        """

        exp_sheets = self._fetch_expense_sheets(spreadsheetId)

        range_names = [f"{sheet['title']}!{RANGE_NAME}" for sheet in exp_sheets]

        result = self._batch_get(spreadsheetId, range_names)
        valueRanges = result.get("valueRanges", [])

        expenses = self._format_expenses_date(exp_sheets, valueRanges)

        return {"expenses": expenses}
