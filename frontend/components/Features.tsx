const features = [
  { icon: '🌍', title: '99 Languages', desc: 'Whisper automatically detects and transcribes audio in almost any language — no configuration needed.' },
  { icon: '🔒', title: 'Private by Default', desc: 'Your audio is processed on your own server and deleted immediately after transcription. Zero data retention.' },
  { icon: '⚡', title: 'Blazing Accuracy', desc: 'State-of-the-art Whisper models handle accents, background noise, and varying audio quality with ease.' },
  { icon: '📦', title: '5 Model Sizes', desc: 'From tiny (lightning fast) to large (best accuracy) — tune the tradeoff for your needs.' },
  { icon: '🚀', title: 'Self-Hosted', desc: 'Deploy to Railway, Render, or any Docker host. Full control, no SaaS fees, no vendor lock-in.' },
  { icon: '☁️', title: 'API Mode', desc: "No GPU? Swap in the OpenAI Whisper API with a single env variable. Same interface, zero code changes." },
]

export default function Features() {
  return (
    <div id="features" className="section-wrap alt">
      <div className="section-inner">
        <div className="section-eyebrow">Why AudioScript</div>
        <h2 className="section-title">Built for Privacy<br />&amp; Performance</h2>
        <p className="section-sub">
          AudioScript runs entirely on your infrastructure.
          No third party ever sees your audio or your transcripts.
        </p>
        <div className="features-grid">
          {features.map((f) => (
            <div key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
