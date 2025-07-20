FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock* /app/
COPY README.md /app/
COPY python_backend /app/python_backend
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
COPY . /app/

# Default command (override in docker-compose)
CMD ["poetry", "run", "uvicorn", "python_backend:app", "--host", "0.0.0.0", "--port", "8000"]
