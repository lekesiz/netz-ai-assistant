# Multi-stage build for NETZ AI
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 netzai && \
    mkdir -p /app /data /logs /backups && \
    chown -R netzai:netzai /app /data /logs /backups

# Copy installed packages from builder
COPY --from=builder /root/.local /home/netzai/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=netzai:netzai . .

# Set Python path
ENV PATH=/home/netzai/.local/bin:$PATH
ENV PYTHONPATH=/app

# Switch to non-root user
USER netzai

# Create necessary directories
RUN mkdir -p /data/netz_ai/rag_storage \
    /data/netz_ai/uploads \
    /logs/netz_ai \
    /backups/netz_ai

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "simple_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]