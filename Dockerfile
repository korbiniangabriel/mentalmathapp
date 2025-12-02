# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY main.py ./
COPY src ./src
COPY .streamlit ./.streamlit
COPY README.md ./

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose Streamlit default port
EXPOSE 8501

# Health check to ensure container is running properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
