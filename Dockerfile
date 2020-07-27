# poetryからpipモジュールを取り出す
FROM python:3.8.5-slim as builder

RUN pip install poetry==1

WORKDIR /work

COPY poetry.lock pyproject.toml ./

RUN poetry export -f requirements.txt -o requirements.txt
RUN poetry export --dev -f requirements.txt -o requirements-dev.txt

# 実行環境ベース
FROM python:3.8.5-alpine as runbase

ENV PYTHONUNBUFFERED=1

WORKDIR /work

COPY --from=builder /work/requirements.txt .

RUN apk add --no-cache gcc=~8.3 libc-dev=~0.7 make=~4.2
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

RUN addgroup -S app && \
    adduser -S app app && \
    chown -R app:app /app

# テスト環境
FROM runbase as tester

COPY --from=builder /work/requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

WORKDIR /app

USER app

COPY kakeibo_exporter/ ./kakeibo_exporter/
COPY tests/ ./tests/

CMD ["pytest", "-s", "--cov"]

# 実行環境
FROM runbase as runner

WORKDIR /app

USER app

COPY kakeibo_exporter/ ./kakeibo_exporter/