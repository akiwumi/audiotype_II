const steps = [
  {
    icon: '📁',
    title: 'Upload Your File',
    desc: 'Drag & drop or browse for any audio or video file. MP3, WAV, M4A, MP4, OGG, FLAC, WEBM, and AAC are all supported.',
  },
  {
    icon: '⚡',
    title: 'Whisper Transcribes',
    desc: "OpenAI's Whisper model processes your audio on your own server with state-of-the-art accuracy. Language is detected automatically.",
  },
  {
    icon: '📄',
    title: 'Copy or Download',
    desc: 'Your transcript appears instantly. Copy to clipboard or download as a .txt file. Your audio is never saved.',
  },
]

export default function HowItWorks() {
  return (
    <div id="how-it-works" className="section-wrap">
      <div className="section-inner">
        <div className="section-eyebrow">Dead Simple</div>
        <h2 className="section-title">Three Steps.<br />That&apos;s It.</h2>
        <p className="section-sub">
          No accounts. No subscriptions. No complexity. Just audio in, text out.
        </p>
        <div className="steps-grid">
          {steps.map((s, i) => (
            <div key={i} className="step-card">
              <div className="step-num">{i + 1}</div>
              <div className="step-icon">{s.icon}</div>
              <div className="step-title">{s.title}</div>
              <div className="step-desc">{s.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
