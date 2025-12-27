FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libpq-dev \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY matrix_architect ./matrix_architect

# Create workspace directory
RUN mkdir -p /workspace

# Expose port
EXPOSE 8080

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "matrix_architect.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
