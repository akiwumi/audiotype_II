export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <div className="footer-brand-name">AudioScript<span>.</span></div>
          <div className="footer-tagline">
            Self-hosted audio transcription.<br />
            Powered by OpenAI Whisper.<br />
            Your server. Your data. Always.
          </div>
        </div>
        <div>
          <div className="footer-col-label">Deploy</div>
          <div className="footer-links">
            <a href="https://railway.app" target="_blank" rel="noopener noreferrer">Railway (Recommended) ↗</a>
            <a href="https://render.com" target="_blank" rel="noopener noreferrer">Render ↗</a>
            <a href="https://vercel.com" target="_blank" rel="noopener noreferrer">Vercel (Frontend) ↗</a>
          </div>
        </div>
        <div>
          <div className="footer-col-label">Stack</div>
          <div className="footer-links">
            <a href="https://nextjs.org" target="_blank" rel="noopener noreferrer">Next.js ↗</a>
            <a href="https://fastapi.tiangolo.com" target="_blank" rel="noopener noreferrer">FastAPI ↗</a>
            <a href="https://github.com/openai/whisper" target="_blank" rel="noopener noreferrer">OpenAI Whisper ↗</a>
          </div>
        </div>
      </div>
      <hr className="footer-divider" />
      <div className="footer-bottom">
        <div className="footer-copy">© 2025 AudioScript. All rights reserved.</div>
        <div className="footer-copy">Next.js + FastAPI + Whisper · MIT License</div>
      </div>
    </footer>
  )
}
