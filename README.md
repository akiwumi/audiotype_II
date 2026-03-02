# AudioScript – Audio to Text Transcriber

A self-hosted web app that transcribes audio to text using OpenAI Whisper.
Runs fully on your own server — no external API required unless you want it.

---

## Why You Can't Use Netlify or Vercel Directly

Netlify and Vercel are **serverless platforms** — they only run short-lived functions (max 10–60 seconds, max ~50 MB). Whisper is a full Python ML model (~150 MB+) that takes minutes to process long audio. It **cannot run on Netlify or Vercel**.

The solution is a **split architecture**:

```
┌─────────────────────────┐        ┌──────────────────────────────┐
│  Frontend (static HTML) │  ───►  │  Backend (FastAPI + Whisper) │
│  Vercel or Netlify      │        │  Railway or Render           │
└─────────────────────────┘        └──────────────────────────────┘
                                            │
                                   ┌────────▼────────┐
                                   │  Supabase (DB)  │  ← optional
                                   │  Store results  │
                                   └─────────────────┘
```

---

## Hosting Options Compared

| Platform     | Best for              | Free tier         | Notes                              |
|--------------|-----------------------|-------------------|------------------------------------|
| **Railway**  | Backend (recommended) | $5/month credit   | Docker support, easy deploys, fast |
| **Render**   | Backend (alternative) | Yes (sleeps)      | Free tier sleeps after 15min idle  |
| **Fly.io**   | Backend (advanced)    | Yes (limited)     | More control, Docker-based         |
| **Vercel**   | Frontend only         | Yes (generous)    | Cannot run Python/Whisper          |
| **Netlify**  | Frontend only         | Yes (generous)    | Cannot run Python/Whisper          |

**Recommended setup for your stack:**
- **Backend → Railway** (handles Docker, long-running processes, no sleep on paid plan)
- **Frontend → Vercel or Netlify** (if you want it separate — or just serve it from Railway)
- **Database → Supabase** (if you want to save transcripts — see section below)

---

## Option A: Deploy Everything to Railway (Simplest)

This is the easiest route. Railway hosts your whole app — frontend and backend together.

### Step 1 — Push your code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/audioscript.git
git push -u origin main
```

### Step 2 — Create a Railway project

1. Go to [railway.app](https://railway.app) and sign up / log in
2. Click **New Project → Deploy from GitHub repo**
3. Select your repo
4. Railway detects the `Dockerfile` and builds automatically

### Step 3 — Set environment variables

In Railway → your service → **Variables**, add:

| Variable         | Value                 |
|------------------|-----------------------|
| `MODEL_SIZE`     | `base`                |
| `MAX_FILE_MB`    | `200`                 |
| `ALLOWED_ORIGINS`| `*` (or your domain)  |

### Step 4 — Get your public URL

Railway auto-generates a URL like `https://audioscript-production.up.railway.app`.
Your app is live at that URL. Done.

---

## Option B: Split — Backend on Railway, Frontend on Vercel/Netlify

Use this if you want to integrate the UI into an existing Vercel/Netlify site.

### Backend on Railway

Follow Option A steps above. Note your Railway URL, e.g.:
`https://audioscript-production.up.railway.app`

### Update the frontend API URL

In `app.py`, find this line in the `<script>` section:

```javascript
const API_BASE = '';
```

Change it to your Railway URL:

```javascript
const API_BASE = 'https://audioscript-production.up.railway.app';
```

Then set the CORS variable in Railway to your Vercel/Netlify domain:

```
ALLOWED_ORIGINS=https://yoursite.vercel.app
```

### Deploy frontend to Vercel

Extract the HTML from `app.py` into a standalone `index.html` file, then:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Or connect your GitHub repo in the Vercel dashboard and it deploys automatically on push.

### Deploy frontend to Netlify

Same approach — create an `index.html` and either drag-drop it in the Netlify UI, or connect your GitHub repo.

---

## Option C: Use OpenAI Whisper API (No GPU Needed)

If you want the cheapest possible backend (no Docker, no heavy server), use OpenAI's hosted Whisper API. Costs $0.006 per minute of audio.

In Railway (or any Node/serverless host), set:

```
USE_OPENAI_API=true
OPENAI_API_KEY=sk-...your key...
```

The rest of the code is identical. This mode works on smaller/cheaper servers since no model runs locally.

---

## Local Development

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install ffmpeg
#    Mac:     brew install ffmpeg
#    Ubuntu:  sudo apt install ffmpeg
#    Windows: https://ffmpeg.org/download.html → add to PATH

# 3. Copy env file
cp .env.example .env

# 4. Run the app
uvicorn app:app --reload
```

Open `http://localhost:8000`

---

## Optional: Save Transcripts to Supabase

If you want to store a history of transcriptions (e.g. per-user history, searchable archive), you can connect to your existing Supabase project.

### Step 1 — Create a table in Supabase

Run this in the Supabase SQL editor:

```sql
create table transcripts (
  id uuid default gen_random_uuid() primary key,
  filename text not null,
  transcript text not null,
  word_count integer,
  created_at timestamptz default now()
);
```

### Step 2 — Add Supabase to requirements.txt

```
supabase>=2.0.0
```

### Step 3 — Add env variables

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
```

### Step 4 — Save transcript after transcription in app.py

Add this to the bottom of the `transcribe()` function, after the Whisper call:

```python
# Optional: save to Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if supabase_url and supabase_key:
    from supabase import create_client
    db = create_client(supabase_url, supabase_key)
    db.table("transcripts").insert({
        "filename": file.filename,
        "transcript": text,
        "word_count": len(text.split()),
    }).execute()
```

---

## Whisper Model Sizes

Change `MODEL_SIZE` in your environment variables:

| Model    | Speed   | Accuracy  | RAM needed |
|----------|---------|-----------|------------|
| `tiny`   | Fastest | Good      | ~1 GB      |
| `base`   | Fast    | Better    | ~1 GB      |
| `small`  | Medium  | Great     | ~2 GB      |
| `medium` | Slower  | Excellent | ~5 GB      |
| `large`  | Slowest | Best      | ~10 GB     |

Start with `base`. Upgrade to `small` or `medium` if accuracy isn't good enough.

---

## File Structure

```
audio-transcriber/
├── app.py              ← Full application (backend + embedded frontend)
├── Dockerfile          ← Container definition for Railway/Render
├── railway.toml        ← Railway deployment config
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variable template
├── .gitignore          ← Excludes .env and cache files
└── README.md           ← This file
```
