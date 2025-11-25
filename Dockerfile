FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY reading_list ./reading_list

COPY alembic.ini .
COPY alembic ./alembic

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 8000

CMD ["uvicorn", "reading_list.main:app", "--host", "0.0.0.0", "--port", "8000"]
