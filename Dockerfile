# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# ffmpeg is required by Whisper for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy app source
COPY app.py .

# Pre-download the Whisper model so first requests aren't slow.
# Set MODEL_SIZE here to match your .env / Railway variable.
ARG MODEL_SIZE=base
RUN python -c "import whisper; whisper.load_model('${MODEL_SIZE}')" || true

# Railway (and most PaaS) injects $PORT at runtime
ENV PORT=8000

EXPOSE $PORT

# Use shell form so $PORT is expanded at runtime
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
