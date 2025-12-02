# if://code/oauth-relay-dockerfile/2025-11-30
# Dockerfile for OAuth Relay Server
# Builds production-ready FastAPI relay server with TLS support

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-relay.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-relay.txt

# Copy application code
COPY src/core/auth/ ./auth/
COPY src/core/auth/oauth_relay_server.py ./

# Create non-root user
RUN useradd -m -u 1000 relay && chown -R relay:relay /app
USER relay

# Expose port
EXPOSE 8443

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f -k https://localhost:8443/health || exit 1

# Start server
CMD ["python", "-m", "oauth_relay_server"]
