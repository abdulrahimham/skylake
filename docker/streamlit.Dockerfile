# ── SkyLake — Streamlit Service ───────────────────────────────
# Runs the Streamlit dashboard on port 8501

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

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit
CMD ["uv", "run", "streamlit", "run", "streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
