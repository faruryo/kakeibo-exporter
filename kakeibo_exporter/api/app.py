
from fastapi import Depends, FastAPI, HTTPException

from kakeibo_exporter.usecase.expense_exporter import ExpenseExporter

app = FastAPI()


class ExpenseExporterFactory:
    expense_exporter: ExpenseExporter

    def set(self, expense_exporter: ExpenseExporter):
        self.expense_exporter = expense_exporter

    def __call__(self) -> ExpenseExporter:
        if not hasattr(self, "expense_exporter"):
            raise Exception(
                "ExpenseExporterインスタンスが設定されていません。"
                "setメソッドでExpenseExporterインスタンスを設定してください。"
            )

        return self.expense_exporter


exporter = ExpenseExporterFactory()


@app.get("/expense/sync/{spreadsheet_id}", response_model=dict)
async def sync_expense(
    spreadsheet_id: str,
    exporter: ExpenseExporter = Depends(exporter)
):
    result = {}
    try:
        result = exporter.sync_sheet2db(spreadsheet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
