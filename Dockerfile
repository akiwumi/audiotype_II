# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch BEFORE openai-whisper.
# The default pip index gives you the full CUDA build (~2.5 GB).
# The CPU wheel is ~800 MB — this single line saves ~2 GB of image size.
RUN pip install --no-cache-dir --prefix=/install \
    torch torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# ffmpeg is required by Whisper for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy app source (index.html is the frontend served by app.py)
COPY app.py index.html ./

# Pre-download the Whisper model so the first request isn't slow.
# Matches the MODEL_SIZE env var you set in Railway → Variables.
ARG MODEL_SIZE=base
RUN python -c "import whisper; whisper.load_model('${MODEL_SIZE}')" || true

# Railway injects $PORT at runtime
ENV PORT=8000
EXPOSE $PORT

CMD uvicorn app:app --host 0.0.0.0 --port $PORT
