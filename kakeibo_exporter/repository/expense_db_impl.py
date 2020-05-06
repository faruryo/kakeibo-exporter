from datetime import date

from sqlalchemy import DATE, Column, Integer, MetaData, String, Table, create_engine
from sqlalchemy.sql import select

from kakeibo_exporter.domain.expense import Expense, Expenses
from kakeibo_exporter.repository.expense_db import ExpenseDb


class ExpenseDbImpl(ExpenseDb):
    def __init__(self, databaseUrl: str, debug: bool = False):

        self.engine = create_engine(databaseUrl, echo=debug)
        metadata = MetaData()
        self.expenses = Table(
            "expenses",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("date", DATE, nullable=False),
            Column("category", String(128), nullable=False),
            Column("debit", String(128), nullable=False),
            Column("credit", String(128), nullable=False),
            Column("price", Integer, nullable=False),
            Column("remark", String(128)),
            mysql_charset="utf8mb4",
        )
        self.expenses.create(self.engine, checkfirst=True)

    def get(self) -> Expenses:
        """支出をすべて取り出す

        Returns:
            int -- すべての支出
        """
        s = select([self.expenses])
        with self.engine.connect() as conn:
            res = Expenses(
                values=[
                    Expense(
                        date=row[self.expenses.c.date],
                        category=row[self.expenses.c.category],
                        debit=row[self.expenses.c.debit],
                        credit=row[self.expenses.c.credit],
                        price=row[self.expenses.c.price],
                        remark=row[self.expenses.c.remark],
                    )
                    for row in conn.execute(s)
                ]
            )
            return res

    def insert(self, expenses: Expenses) -> int:
        """支出をインサートする

        Arguments:
            expenses {Expenses} -- インサートする支出

        Returns:
            int -- インサートに成功した件数
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                self.expenses.insert(),
                [
                    {
                        "date": expense.date,
                        "category": expense.category,
                        "debit": expense.debit,
                        "credit": expense.credit,
                        "price": expense.price,
                        "remark": expense.remark,
                    }
                    for expense in expenses
                ],
            )
            c = result.rowcount if result.rowcount >= 0 else len(expenses)
            return c

    def clean(self):
        with self.engine.connect() as conn:
            conn.execute(self.expenses.delete())

    def delete_by_year(self, year: int) -> int:
        """指定された年の支出を削除する

        Arguments:
            year {int} -- 削除したい年(西暦)

        Returns:
            int -- 削除した件数
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                self.expenses.delete().where(
                    self.expenses.c.date.between(date(year, 1, 1), date(year, 12, 31))
                )
            )
            return result.rowcount
