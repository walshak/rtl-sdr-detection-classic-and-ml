# Multi-stage build for RTL-SDR Detection System
FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    librtlsdr-dev \
    rtl-sdr \
    libusb-1.0-0-dev \
    pkg-config \
    gcc \
    g++ \
    git \
    udev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .
COPY templates/ templates/
COPY baseline.json .

# Create necessary directories
RUN mkdir -p /app/data /app/models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api.py
ENV RTL_SDR_DEVICE=0

# Expose Flask port
EXPOSE 5000

# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]
