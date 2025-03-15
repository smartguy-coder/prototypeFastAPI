FROM python:3.12-slim

WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl gcc libpq-dev make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-ansi --no-root --no-interaction

# Створюємо директорію tmp_uds до переходу на appuser
RUN mkdir -p /app/tmp_uds

# Створюємо групу та користувача
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Задаємо права директорії tmp_uds
RUN chmod 777 /app/tmp_uds

COPY /app /app

USER appuser

EXPOSE 15000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15000"]
