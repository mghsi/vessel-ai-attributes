FROM python:3.10-slim

WORKDIR /app

# Install development tools
RUN pip install --upgrade pip

# Copy backend project files
COPY backend/pyproject.toml ./
COPY backend/ .

# Install dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Create uploads directory
RUN mkdir -p uploads && chmod 777 uploads

# Expose the port the app runs on
EXPOSE 5001

# Default command (will be overridden by docker-compose for development)
CMD ["python", "main.py"]