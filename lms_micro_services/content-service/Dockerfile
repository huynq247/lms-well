FROM python:3.11-slim

WORKDIR /app

# Install system dependencies  
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install direct dependencies first to ensure they're properly installed
RUN pip install --no-cache-dir pydantic-settings==2.1.0 email-validator==2.1.0

# Then install the rest of the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install dependencies again to ensure they're properly installed
RUN pip install --no-cache-dir pydantic-settings==2.1.0 email-validator==2.1.0

# Print installed packages for debugging
RUN pip list

# Copy application code
COPY . .

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the application with detailed logging
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--log-level", "debug"]
