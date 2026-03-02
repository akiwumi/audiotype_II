export default function Nav() {
  return (
    <nav className="nav">
      <a className="nav-logo" href="/">
        AudioScript<span>.</span>
      </a>
      <ul className="nav-links">
        <li><a href="#how-it-works">How It Works</a></li>
        <li><a href="#features">Features</a></li>
        <li><a href="#models">Models</a></li>
      </ul>
      <a className="nav-cta" href="#app-top">Try It Free →</a>
    </nav>
  )
}
