FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (git for optional patch application / cloning)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY matrix_architect /app/matrix_architect

RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .

EXPOSE 8080

CMD ["uvicorn", "matrix_architect.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
