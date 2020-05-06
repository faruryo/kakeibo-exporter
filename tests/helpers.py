

from kakeibo_exporter.domain.expense import Expenses


def count_expenses_year(expenses: Expenses) -> dict:

    year_counts = {}

    for expense in expenses:
        y = expense.date.year
        year_counts[y] = year_counts[y] + 1 if year_counts.get(y) is not None else 1

    return year_counts
