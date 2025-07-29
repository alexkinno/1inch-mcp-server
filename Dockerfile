# Use Python 3.13 slim base image
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_PREFERENCE=only-system
ENV UV_FROZEN=true

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code (needed for local package build)
COPY main.py ./
COPY README.md ./
COPY inch_mcp_server/ ./inch_mcp_server/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Production stage
FROM python:3.13-slim as production

# Set working directory
WORKDIR /app

# Install only curl for health check
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy application code
COPY --chown=app:app . /app

# Make sure the virtual environment is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 8000 for HTTP transport
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["1inch-mcp", "--transport", "streamable-http"]