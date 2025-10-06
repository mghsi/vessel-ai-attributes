FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for matplotlib, pandas, and scientific computing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install development tools
RUN pip install --upgrade pip

# Copy backend project files
COPY backend/pyproject.toml ./
COPY backend/uv.lock* ./

# Install uv for faster package installation
RUN pip install uv

# Copy all backend files
COPY backend/ .

# Install dependencies using uv for faster installation
RUN uv pip install --system --no-cache-dir -e ".[dev]"

# Create required directories
RUN mkdir -p uploads && chmod 777 uploads
RUN mkdir -p data && chmod 777 data

# Set environment variables for matplotlib
ENV MPLBACKEND=Agg
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/v1/health || exit 1

# Default command (will be overridden by docker-compose for development)
CMD ["python", "main.py"]