FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install --upgrade pip \
    && $POETRY_VENV/bin/pip install poetry==1.8.3

ENV PATH="${POETRY_VENV}/bin:${PATH}"

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry lock --no-update 2>/dev/null || poetry lock \
    && poetry install --only main --no-interaction --no-ansi \
    && rm -rf $POETRY_CACHE_DIR

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
