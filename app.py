"""
AudioScript – Audio to Text Transcriber
----------------------------------------
Self-hosted web app powered by OpenAI Whisper (local) or the OpenAI Whisper API.

Environment variables (set in .env or your hosting dashboard):
  MODEL_SIZE       Whisper model: tiny | base | small | medium | large  (default: base)
  USE_OPENAI_API   Set to "true" to use OpenAI's Whisper API instead of local model
  OPENAI_API_KEY   Required only when USE_OPENAI_API=true
  MAX_FILE_MB      Max upload size in MB (default: 200)
  ALLOWED_ORIGINS  Comma-separated CORS origins, e.g. https://myapp.vercel.app
                   Defaults to * (open) — lock this down in production!

Run locally:   uvicorn app:app --reload
Production:    uvicorn app:app --host 0.0.0.0 --port $PORT
"""

import os
import pathlib
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

# ── Config from environment ─────────────────────────────────────────────────
MODEL_SIZE      = os.getenv("MODEL_SIZE", "base")
USE_OPENAI_API  = os.getenv("USE_OPENAI_API", "false").lower() == "true"
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
MAX_FILE_MB     = int(os.getenv("MAX_FILE_MB", "200"))
MAX_FILE_BYTES  = MAX_FILE_MB * 1024 * 1024
RAW_ORIGINS     = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in RAW_ORIGINS.split(",")] if RAW_ORIGINS != "*" else ["*"]

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="AudioScript", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model (only when running locally, not via OpenAI API) ───────────────
whisper_model = None

if not USE_OPENAI_API:
    import whisper
    print(f"Loading Whisper '{MODEL_SIZE}' model… (first run downloads it)")
    whisper_model = whisper.load_model(MODEL_SIZE)
    print("Whisper model ready.")
else:
    if not OPENAI_API_KEY:
        raise RuntimeError("USE_OPENAI_API=true but OPENAI_API_KEY is not set.")
    print("Using OpenAI Whisper API.")

# ── Allowed audio/video extensions ──────────────────────────────────────────
ALLOWED_EXTENSIONS = {
    ".mp3", ".mp4", ".wav", ".m4a", ".ogg",
    ".flac", ".webm", ".mpeg", ".mpga", ".aac",
}

# ── HTML Frontend ────────────────────────────────────────────────────────────
# Reads index.html from the project directory.
# If you want to deploy the frontend separately (Vercel/Netlify), use index.html
# directly and update API_BASE inside it to point to your Railway URL.
_html_file = pathlib.Path(__file__).parent / "index.html"
HTML = _html_file.read_text(encoding="utf-8") if _html_file.exists() else """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AudioScript – Audio to Text</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f6fa; color: #2d2d2d; min-height: 100vh;
    }

    /* Nav */
    nav {
      background: #fff; border-bottom: 1px solid #e8e8e8;
      padding: 0 40px; height: 60px;
      display: flex; align-items: center; justify-content: space-between;
    }
    .logo { font-size: 1.3rem; font-weight: 800; color: #5b5ef4; }
    .logo span { color: #2d2d2d; }
    .nav-tag {
      font-size: 0.78rem; background: #f0f0ff; color: #5b5ef4;
      border-radius: 99px; padding: 4px 12px; font-weight: 600;
    }

    /* Hero */
    .hero { text-align: center; padding: 56px 20px 24px; }
    .hero h1 { font-size: 2.2rem; font-weight: 800; margin-bottom: 12px; }
    .hero p { color: #666; font-size: 1.05rem; max-width: 500px; margin: 0 auto 40px; }

    /* Upload */
    .upload-wrapper { max-width: 680px; margin: 0 auto 40px; padding: 0 20px; }
    .drop-zone {
      border: 2px dashed #c5c5f0; border-radius: 16px; background: #fff;
      padding: 50px 30px; text-align: center; transition: all 0.2s ease;
      cursor: pointer; position: relative;
    }
    .drop-zone.dragover { border-color: #5b5ef4; background: #f0f0ff; }
    .drop-zone input[type="file"] {
      position: absolute; inset: 0; opacity: 0; cursor: pointer;
      width: 100%; height: 100%;
    }
    .drop-icon { font-size: 2.6rem; margin-bottom: 16px; }
    .drop-zone h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
    .drop-zone p { color: #888; font-size: 0.9rem; margin-bottom: 20px; }
    .choose-btn {
      background: #5b5ef4; color: #fff; border: none; border-radius: 8px;
      padding: 12px 28px; font-size: 1rem; font-weight: 600;
      cursor: pointer; pointer-events: none;
    }
    .file-note { margin-top: 14px; font-size: 0.82rem; color: #aaa; }

    /* Status */
    #status-section { max-width: 680px; margin: 0 auto 30px; padding: 0 20px; display: none; }
    .status-card {
      background: #fff; border-radius: 12px; padding: 24px 28px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .file-info { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
    .file-icon { font-size: 1.6rem; }
    .file-name { font-weight: 600; font-size: 0.95rem; }
    .file-size { font-size: 0.82rem; color: #999; }
    .progress-bar-outer {
      background: #eee; border-radius: 999px; height: 8px;
      overflow: hidden; margin-bottom: 10px;
    }
    .progress-bar-inner {
      background: linear-gradient(90deg, #5b5ef4, #8b8ef8);
      height: 100%; width: 0%; border-radius: 999px;
      transition: width 0.5s ease;
      animation: pulse 1.8s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.65 } }
    .status-text { font-size: 0.88rem; color: #666; }

    /* Result */
    #result-section { max-width: 680px; margin: 0 auto 60px; padding: 0 20px; display: none; }
    .result-card {
      background: #fff; border-radius: 12px; padding: 28px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .result-header {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
    }
    .result-header h3 { font-size: 1rem; font-weight: 700; }
    .result-actions { display: flex; gap: 10px; }
    .btn-secondary {
      background: #f0f0ff; color: #5b5ef4; border: none; border-radius: 7px;
      padding: 8px 16px; font-size: 0.88rem; font-weight: 600; cursor: pointer;
    }
    .btn-secondary:hover { background: #e4e4fb; }
    .btn-primary {
      background: #5b5ef4; color: #fff; border: none; border-radius: 7px;
      padding: 8px 16px; font-size: 0.88rem; font-weight: 600; cursor: pointer;
    }
    .btn-primary:hover { background: #4749d4; }
    #transcript-box {
      background: #f9f9ff; border: 1px solid #e8e8f0; border-radius: 10px;
      padding: 18px; font-size: 0.95rem; line-height: 1.75; color: #333;
      white-space: pre-wrap; min-height: 120px; max-height: 440px; overflow-y: auto;
    }
    .word-count { margin-top: 10px; font-size: 0.82rem; color: #aaa; text-align: right; }
    .try-again-btn {
      display: block; margin: 20px auto 0; background: none;
      border: 2px solid #e0e0e0; border-radius: 8px; padding: 10px 24px;
      font-size: 0.9rem; color: #666; cursor: pointer; font-weight: 600;
    }
    .try-again-btn:hover { border-color: #5b5ef4; color: #5b5ef4; }

    /* Features */
    .features {
      max-width: 900px; margin: 0 auto 80px; padding: 0 20px;
      display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px;
    }
    .feature-card {
      background: #fff; border-radius: 12px; padding: 28px 24px;
      text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    .feature-card .icon { font-size: 2rem; margin-bottom: 14px; }
    .feature-card h4 { font-size: 1rem; font-weight: 700; margin-bottom: 8px; }
    .feature-card p { font-size: 0.88rem; color: #777; line-height: 1.6; }

    /* Toast */
    .toast {
      position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
      background: #2d2d2d; color: #fff; padding: 12px 24px; border-radius: 8px;
      font-size: 0.9rem; opacity: 0; transition: opacity 0.3s;
      pointer-events: none; z-index: 9999;
    }
    .toast.show { opacity: 1; }
  </style>
</head>
<body>

  <nav>
    <div class="logo">Audio<span>Script</span></div>
    <div class="nav-tag">Powered by Whisper</div>
  </nav>

  <div class="hero">
    <h1>Audio to Text, Instantly</h1>
    <p>Upload any audio or video file and get an accurate transcript in seconds.</p>
  </div>

  <!-- Upload Zone -->
  <div class="upload-wrapper">
    <div class="drop-zone" id="dropZone">
      <input type="file" id="fileInput"
        accept="audio/*,video/*,.mp3,.mp4,.wav,.m4a,.ogg,.flac,.webm,.aac" />
      <div class="drop-icon">🎙️</div>
      <h2>Drag & drop your audio file here</h2>
      <p>MP3, MP4, WAV, M4A, OGG, FLAC, WEBM, AAC supported</p>
      <button class="choose-btn">Choose File</button>
      <div class="file-note">Files are processed securely and never stored.</div>
    </div>
  </div>

  <!-- Processing Status -->
  <div id="status-section">
    <div class="status-card">
      <div class="file-info">
        <div class="file-icon">🎵</div>
        <div>
          <div class="file-name" id="status-filename"></div>
          <div class="file-size" id="status-filesize"></div>
        </div>
      </div>
      <div class="progress-bar-outer">
        <div class="progress-bar-inner" id="progress-bar"></div>
      </div>
      <div class="status-text" id="status-text">Uploading…</div>
    </div>
  </div>

  <!-- Transcript Result -->
  <div id="result-section">
    <div class="result-card">
      <div class="result-header">
        <h3>✅ Transcript Ready</h3>
        <div class="result-actions">
          <button class="btn-secondary" onclick="copyText()">Copy</button>
          <button class="btn-primary" onclick="downloadText()">Download .txt</button>
        </div>
      </div>
      <div id="transcript-box"></div>
      <div class="word-count" id="word-count"></div>
    </div>
    <button class="try-again-btn" onclick="resetApp()">↩ Transcribe another file</button>
  </div>

  <!-- Feature Cards -->
  <div class="features">
    <div class="feature-card">
      <div class="icon">🌍</div>
      <h4>99 Languages</h4>
      <p>Whisper automatically detects and transcribes audio in almost any language.</p>
    </div>
    <div class="feature-card">
      <div class="icon">🔒</div>
      <h4>Private by Default</h4>
      <p>Audio is processed on your server. Files are deleted immediately after transcription.</p>
    </div>
    <div class="feature-card">
      <div class="icon">⚡</div>
      <h4>Fast & Accurate</h4>
      <p>State-of-the-art accuracy across accents, noise, and audio conditions.</p>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    // ── Config ──────────────────────────────────────────────────────────────
    // If you host backend separately, replace with your Railway/Render URL:
    const API_BASE = '';  // e.g. 'https://audioscript.railway.app'

    // ── State ───────────────────────────────────────────────────────────────
    const dropZone  = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    let currentFilename = '';

    // ── Drag & Drop ─────────────────────────────────────────────────────────
    dropZone.addEventListener('dragover', e => {
      e.preventDefault(); dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
      e.preventDefault(); dropZone.classList.remove('dragover');
      if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files[0]) handleFile(fileInput.files[0]);
    });

    // ── Main flow ────────────────────────────────────────────────────────────
    function handleFile(file) {
      currentFilename = file.name;
      showStatus(file);
      uploadAndTranscribe(file);
    }

    function showStatus(file) {
      document.querySelector('.upload-wrapper').style.display = 'none';
      document.getElementById('result-section').style.display = 'none';
      document.getElementById('status-section').style.display = 'block';
      document.getElementById('status-filename').textContent = file.name;
      document.getElementById('status-filesize').textContent =
        (file.size / 1024 / 1024).toFixed(2) + ' MB';
      setProgress(20, 'Uploading file…');
    }

    function setProgress(pct, msg) {
      document.getElementById('progress-bar').style.width = pct + '%';
      document.getElementById('status-text').textContent = msg;
    }

    async function uploadAndTranscribe(file) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        setProgress(40, 'File received. Transcribing audio…');
        let pct = 42;
        const ticker = setInterval(() => {
          if (pct < 88) {
            pct += 3;
            setProgress(pct, 'Transcribing… (larger files take a minute)');
          }
        }, 2500);

        const res = await fetch(API_BASE + '/transcribe', {
          method: 'POST', body: formData
        });
        clearInterval(ticker);

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Transcription failed');
        }
        const data = await res.json();
        setProgress(100, 'Done!');
        setTimeout(() => showResult(data.text), 500);
      } catch (err) {
        document.getElementById('status-section').style.display = 'none';
        document.querySelector('.upload-wrapper').style.display = 'block';
        showToast('Error: ' + err.message);
      }
    }

    function showResult(text) {
      document.getElementById('status-section').style.display = 'none';
      document.getElementById('result-section').style.display = 'block';
      document.getElementById('transcript-box').textContent = text.trim();
      const words = text.trim().split(/\s+/).filter(Boolean).length;
      document.getElementById('word-count').textContent =
        words + ' words · ' + text.trim().length + ' characters';
    }

    function copyText() {
      navigator.clipboard.writeText(
        document.getElementById('transcript-box').textContent
      ).then(() => showToast('Copied to clipboard!'));
    }

    function downloadText() {
      const text = document.getElementById('transcript-box').textContent;
      const blob = new Blob([text], { type: 'text/plain' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = currentFilename.replace(/\.[^.]+$/, '') + '_transcript.txt';
      a.click();
    }

    function resetApp() {
      document.getElementById('result-section').style.display = 'none';
      document.querySelector('.upload-wrapper').style.display = 'block';
      fileInput.value = '';
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg; t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 3500);
    }
  </script>
</body>
</html>
"""


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_SIZE, "mode": "openai_api" if USE_OPENAI_API else "local"}


# ── Serve frontend ────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


# ── Transcribe endpoint ───────────────────────────────────────────────────────
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: '{ext}'")

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {MAX_FILE_MB} MB."
        )

    tmp_path = None
    try:
        # Write to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        if USE_OPENAI_API:
            text = _transcribe_via_openai_api(tmp_path, file.filename)
        else:
            text = _transcribe_local(tmp_path)

        return JSONResponse({"text": text})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _transcribe_local(path: str) -> str:
    result = whisper_model.transcribe(path)
    return result["text"]


def _transcribe_via_openai_api(path: str, filename: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    with open(path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, f),
        )
    return response.text
