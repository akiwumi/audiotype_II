# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch BEFORE openai-whisper.
# Railway has no GPU — the default CUDA wheel is ~2.5 GB and causes build
# timeouts. The CPU wheel is ~800 MB and works identically on Railway.
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

# Copy app source — index.html is the frontend UI served by app.py
COPY app.py index.html ./

# Railway injects $PORT at runtime
ENV PORT=8000
EXPOSE $PORT

CMD uvicorn app:app --host 0.0.0.0 --port $PORT
