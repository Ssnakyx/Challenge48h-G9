# ============================================================================
# Stage 1: Builder - Compile Python dependencies as wheels
# ============================================================================
FROM python:3.11 AS builder

WORKDIR /usr/src/app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels (no cache for reproducibility)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# ============================================================================
# Stage 2: Final - Slim Python runtime with pre-built wheels
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder stage
COPY --from=builder /usr/src/app/wheels /usr/src/app/wheels

# Install dependencies from wheels (no network call needed)
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /usr/src/app/wheels/*

# Copy application source code
COPY . .

# Default: run uvicorn (can be overridden in docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
