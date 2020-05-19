
import os

import typer
import uvicorn

from kakeibo_exporter.api.app import app as api_app
from kakeibo_exporter.api.app import exporter as exporter_factory
from kakeibo_exporter.driver.sheet_driver_impl import SheetDriverImpl
from kakeibo_exporter.repository.expense_db_impl import ExpenseDbImpl
from kakeibo_exporter.repository.expense_sheet_impl import ExpenseSheetImpl
from kakeibo_exporter.usecase.expense_exporter import ExpenseExporter
from kakeibo_exporter.usecase.expense_exporter_impl import ExpenseExporterImpl

app = typer.Typer()


# TODO: PyPIリポジトリ作成
# TODO: ロガーを導入してログを吐き出す
def getDbUrl(user: str, passwd: str, host: str, db: str) -> str:

    user = user or os.environ.get("MYSQL_USER")
    if not user:
        raise typer.BadParameter('user未指定')

    passwd = passwd if passwd is not None else os.environ.get("MYSQL_PASSWORD")
    if passwd is None:
        raise typer.BadParameter('passwd未指定')

    host = host or os.environ.get("MYSQL_HOST")
    if not host:
        raise typer.BadParameter('host未指定')

    db = db or os.environ.get("MYSQL_DATABASE")
    if not db:
        raise typer.BadParameter('db未指定')

    dbUrl = "mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8mb4" % (
        user,
        passwd,
        host,
        db,
    )

    return dbUrl


def getExporter(user: str, passwd: str, host: str, db: str) -> ExpenseExporter:
    dbUrl = getDbUrl(
        user,
        passwd,
        host,
        db,
    )

    exporter = ExpenseExporterImpl(
        sheet=ExpenseSheetImpl(sheet_driver=SheetDriverImpl()),
        db=ExpenseDbImpl(dbUrl),
    )

    return exporter


@app.command()
def export_expense(
    user: str = typer.Option(None, help="MySQLのユーザ名"),
    passwd: str = typer.Option(None, help="MySQLのパスワード"),
    host: str = typer.Option(None, help="MySQLのホスト名"),
    db: str = typer.Option(None, help="MySQLのデータベース名"),
    spreadsheetid: str = typer.Argument(...),
):
    """
    支出情報を指定されたスプレッドシートからDBに出力する

    DB情報はそれぞれ環境変数でも設定可能
    """

    exporter = getExporter(
        user,
        passwd,
        host,
        db,
    )

    result = exporter.export_sheet2db(spreadsheetid)
    print(result)


@app.command()
def sync_expense(
    user: str = typer.Option(None, help="MySQLのユーザ名"),
    passwd: str = typer.Option(None, help="MySQLのパスワード"),
    host: str = typer.Option(None, help="MySQLのホスト名"),
    db: str = typer.Option(None, help="MySQLのデータベース名"),
    spreadsheetid: str = typer.Argument(...),
):
    """
    支出情報を指定されたスプレッドシートからDBに同期する

    DB情報はそれぞれ環境変数でも設定可能
    """
    exporter = getExporter(
        user,
        passwd,
        host,
        db,
    )

    result = exporter.sync_sheet2db(spreadsheetid)
    print(result)


@app.command()
def db_clean(
    user: str = typer.Option(None, help="MySQLのユーザ名"),
    passwd: str = typer.Option(None, help="MySQLのパスワード"),
    host: str = typer.Option(None, help="MySQLのホスト名"),
    db: str = typer.Option(None, help="MySQLのデータベース名"),
):
    """
    支出情報DBのデータを全て削除する

    DB情報はそれぞれ環境変数でも設定可能
    """

    exporter = getExporter(
        user,
        passwd,
        host,
        db,
    )

    exporter.db_clean()


@app.command()
def run_api(
    user: str = typer.Option(None, help="MySQLのユーザ名"),
    passwd: str = typer.Option(None, help="MySQLのパスワード"),
    host: str = typer.Option(None, help="MySQLのホスト名"),
    db: str = typer.Option(None, help="MySQLのデータベース名"),
    port: int = typer.Option(8080, help="APIのポート番号"),
):
    """
    APIサーバを起動する

    DB情報はそれぞれ環境変数でも設定可能
    """

    exporter = getExporter(
        user,
        passwd,
        host,
        db,
    )

    exporter_factory.set(exporter)

    uvicorn.run(app=api_app, port=port, host="0.0.0.0")


def main():
    app()


if __name__ == "__main__":
    main()
