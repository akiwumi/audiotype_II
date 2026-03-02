'use client'

import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from 'react'

type Panel = 'upload' | 'processing' | 'result'

export default function AppPanel() {
  const [panel, setPanel]               = useState<Panel>('upload')
  const [filename, setFilename]         = useState('')
  const [filesize, setFilesize]         = useState('')
  const [progress, setProgress]         = useState(0)
  const [progressText, setProgressText] = useState('Uploading…')
  const [transcript, setTranscript]     = useState('')
  const [wordCount, setWordCount]       = useState('')
  const [toast, setToast]               = useState('')
  const [isDragging, setIsDragging]     = useState(false)

  const fileInputRef  = useRef<HTMLInputElement>(null)
  const currentFile   = useRef('')

  // ── Toast ────────────────────────────────────────────────────────────────
  const showToast = useCallback((msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(''), 3500)
  }, [])

  // ── Core upload + transcribe flow ────────────────────────────────────────
  const handleFile = useCallback(async (file: File) => {
    currentFile.current = file.name
    setFilename(file.name)
    setFilesize((file.size / 1024 / 1024).toFixed(2) + ' MB')
    setProgress(18)
    setProgressText('Uploading file…')
    setPanel('processing')

    const formData = new FormData()
    formData.append('file', file)

    try {
      setProgress(38)
      setProgressText('File received. Starting transcription…')

      let pct = 40
      const ticker = setInterval(() => {
        if (pct < 87) {
          pct += Math.random() * 4 + 1
          setProgress(Math.min(pct, 87))
          setProgressText('Transcribing… (larger files take longer)')
        }
      }, 2800)

      const res = await fetch('/api/transcribe', { method: 'POST', body: formData })
      clearInterval(ticker)

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(err.detail ?? 'Transcription failed')
      }

      const data = await res.json()
      setProgress(100)
      setProgressText('Done!')

      setTimeout(() => {
        const clean = (data.text as string).trim()
        const words = clean.split(/\s+/).filter(Boolean).length
        setTranscript(clean)
        setWordCount(
          `${words.toLocaleString()} words · ${clean.length.toLocaleString()} characters`
        )
        setPanel('result')
      }, 550)
    } catch (err) {
      setPanel('upload')
      showToast(`Error: ${(err as Error).message}`)
    }
  }, [showToast])

  // ── Drag & drop ──────────────────────────────────────────────────────────
  const onDragOver  = useCallback((e: DragEvent<HTMLDivElement>) => { e.preventDefault(); setIsDragging(true) }, [])
  const onDragLeave = useCallback(() => setIsDragging(false), [])
  const onDrop      = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0])
  }, [handleFile])

  const onInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) handleFile(e.target.files[0])
  }, [handleFile])

  // ── Result actions ───────────────────────────────────────────────────────
  const copyText = useCallback(() => {
    navigator.clipboard.writeText(transcript).then(() => showToast('Copied to clipboard!'))
  }, [transcript, showToast])

  const downloadText = useCallback(() => {
    const blob = new Blob([transcript], { type: 'text/plain' })
    const a    = document.createElement('a')
    a.href     = URL.createObjectURL(blob)
    a.download = currentFile.current.replace(/\.[^.]+$/, '') + '_transcript.txt'
    a.click()
  }, [transcript])

  const reset = useCallback(() => {
    setPanel('upload')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }, [])

  return (
    <>
      <div className="hero-app-panel">

        {/* ── STATE 1: Upload ───────────────────────────────────────────── */}
        {panel === 'upload' && (
          <>
            <div className="panel-label">Drop &amp; Transcribe</div>
            <div
              className={`drop-zone${isDragging ? ' dragover' : ''}`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*,video/*,.mp3,.mp4,.wav,.m4a,.ogg,.flac,.webm,.aac"
                onChange={onInputChange}
                style={{ display: 'none' }}
              />
              <div className="dz-icon">🎙️</div>
              <div className="dz-title">Drag your file here</div>
              <div className="dz-sub">or click anywhere to browse</div>
              <button
                className="dz-btn"
                onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click() }}
              >
                Choose File
              </button>
              <div className="dz-formats">MP3 · WAV · M4A · MP4 · OGG · FLAC · WEBM · AAC</div>
              <div className="dz-secure">🔒 Files are never stored — deleted after transcription</div>
            </div>
          </>
        )}

        {/* ── STATE 2: Processing ───────────────────────────────────────── */}
        {panel === 'processing' && (
          <>
            <div className="panel-label">Transcribing…</div>
            <div className="proc-file">
              <div className="proc-icon">🎵</div>
              <div>
                <div className="proc-name">{filename}</div>
                <div className="proc-size">{filesize}</div>
              </div>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <div className="progress-label">{progressText}</div>
          </>
        )}

        {/* ── STATE 3: Result ───────────────────────────────────────────── */}
        {panel === 'result' && (
          <>
            <div className="panel-label">Your Transcript</div>
            <div className="result-header">
              <div className="result-title-row">
                Ready <span className="done-badge">DONE</span>
              </div>
              <div className="result-btns">
                <button className="btn-ghost" onClick={copyText}>Copy</button>
                <button className="btn-solid" onClick={downloadText}>Download .txt ↓</button>
              </div>
            </div>
            <div className="transcript-box">{transcript}</div>
            <div className="word-count">{wordCount}</div>
            <button className="reset-btn" onClick={reset}>↩ Transcribe Another File</button>
          </>
        )}

      </div>

      {/* Toast — position:fixed so location in DOM doesn't matter */}
      <div className={`toast${toast ? ' show' : ''}`}>{toast}</div>
    </>
  )
}
