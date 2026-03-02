const models = [
  { name: 'tiny',   speed: 'Fastest', speedColor: 'var(--orange)', accuracy: 'Good',      ram: '~1 GB',  recommended: false },
  { name: 'base',   speed: 'Fast',    speedColor: undefined,       accuracy: 'Better',    ram: '~1 GB',  recommended: true  },
  { name: 'small',  speed: 'Medium',  speedColor: undefined,       accuracy: 'Great',     ram: '~2 GB',  recommended: false },
  { name: 'medium', speed: 'Slower',  speedColor: undefined,       accuracy: 'Excellent', ram: '~5 GB',  recommended: false },
  { name: 'large',  speed: 'Slowest', speedColor: 'var(--gray)',   accuracy: 'Best',      ram: '~10 GB', recommended: false },
]

export default function ModelTable() {
  return (
    <div id="models" className="section-wrap">
      <div className="section-inner">
        <div className="section-eyebrow">Configuration</div>
        <h2 className="section-title">Speed vs. Accuracy —<br />You Decide</h2>
        <p className="section-sub">
          Set the <code>MODEL_SIZE</code> environment variable on your server.
          Start with <code>base</code> — it&apos;s fast and accurate enough for most use cases.
        </p>
        <div style={{ overflowX: 'auto' }}>
          <table className="model-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Speed</th>
                <th>Accuracy</th>
                <th>RAM Needed</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.name} className={m.recommended ? 'recommended' : undefined}>
                  <td>
                    <code>{m.name}</code>
                    {m.recommended && <span className="model-tag">Recommended</span>}
                  </td>
                  <td style={m.speedColor ? { color: m.speedColor, fontWeight: 700 } : undefined}>
                    {m.speed}
                  </td>
                  <td>{m.accuracy}</td>
                  <td style={{ color: 'var(--gray)' }}>{m.ram}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
