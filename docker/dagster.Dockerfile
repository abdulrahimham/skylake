# ── SkyLake — Dagster Service ─────────────────────────────────
# Runs the Dagster orchestrator and UI on port 3000

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency file first (for Docker layer caching)
COPY pyproject.toml .

# Install project dependencies
RUN uv sync --extra dev

# Copy the rest of the project
COPY . .

# Expose Dagster UI port
EXPOSE 3000

# Start Dagster
CMD ["uv", "run", "dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
