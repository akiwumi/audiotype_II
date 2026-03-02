import AppPanel from './AppPanel'

export default function Hero() {
  return (
    <section className="hero" id="app-top">
      <div className="hero-inner">

        {/* Left: Marketing copy */}
        <div className="hero-copy">
          <div className="hero-eyebrow">Powered by OpenAI Whisper</div>
          <h1 className="hero-h1">
            Turn <em>Audio</em>
            <br />
            Into Text.
          </h1>
          <p className="hero-sub">
            Upload any audio or video file and get an accurate, readable transcript in
            seconds. 99 languages. Fully private. Runs on your server.
          </p>
          <div className="hero-actions">
            <a className="btn-hero" href="#app-top">Upload a File ↗</a>
            <span className="hero-note">MP3, WAV, M4A, MP4 &amp; more</span>
          </div>
        </div>

        {/* Right: Interactive app panel */}
        <div>
          <AppPanel />
        </div>

      </div>
    </section>
  )
}
