# Use Python 3.11 official image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8012

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=main.py

# Start command - Use python -m to properly handle package imports
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8012"]
