# Legacy AI Modernizer - Dockerfile
# Build: docker build -t legacy-ai-modernizer .
# Run:   docker run -it legacy-ai-modernizer

FROM python:3.12-slim

LABEL maintainer="Lebrin"
LABEL description="AI agent that safely modernizes legacy Python code"
LABEL version="0.1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
COPY sample_legacy/ ./sample_legacy/

# Create directories
RUN mkdir -p reports patches

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

# Run tests to validate installation
RUN pytest sample_legacy/tests/ -v --tb=short

# Default command
CMD ["modernizer", "--help"]
