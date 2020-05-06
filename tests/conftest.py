from datetime import date, timedelta
from typing import Callable

import pytest

from kakeibo_exporter.domain.expense import Expense, Expenses


@pytest.fixture
def expense_one() -> Expense:
    return Expenses(
        [
            Expense(
                date=date(2020, 1, 1),
                category="食費(買い出し)",
                debit="すき家",
                credit="村田",
                price=1270,
                remark="",
            )
        ]
    )


@pytest.fixture
def create_expenses_b2d() -> Callable:
    def _create_expenses_b2d(from_date: date, to_date: date) -> Expenses:
        if from_date >= to_date:
            raise Exception(f"引数の日付大小関係が逆転しています。{from_date} >= {to_date}")

        return Expenses(
            values=[
                Expense(
                    date=from_date + timedelta(i),
                    category="食費(買い出し)",
                    debit="すき家",
                    credit="村田",
                    price=1270,
                    remark="",
                )
                for i in range((to_date - from_date).days + 1)
            ]
        )

    return _create_expenses_b2d
