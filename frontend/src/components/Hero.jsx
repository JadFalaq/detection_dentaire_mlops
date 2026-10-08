import { EXAMPLE_EVENT } from '../events'
import { useI18n } from '../i18n/context'
import { CheckIcon } from './Icons'
import XRayArt from './XRayArt'

export default function Hero() {
  const { t } = useI18n()

  function tryExample() {
    window.dispatchEvent(new CustomEvent(EXAMPLE_EVENT))
    document.getElementById('analyse')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section className="hero" id="top">
      <div className="container hero-grid">
        <div className="hero-copy">
          <span className="eyebrow">{t.hero.eyebrow}</span>
          <h1>
            {t.hero.titleStart} <span className="accent">{t.hero.titleAccent}</span>
          </h1>
          <p className="darija">«&#8239;{t.hero.darija}&#8239;»</p>
          <p className="lead">{t.hero.lead}</p>
          <div className="hero-ctas">
            <a href="#analyse" className="btn btn-primary btn-lg">
              {t.hero.ctaPrimary}
            </a>
            <button type="button" className="btn btn-ghost btn-lg" onClick={tryExample}>
              {t.hero.ctaSecondary}
            </button>
          </div>
          <ul className="trust-list">
            {t.hero.trust.map((item) => (
              <li key={item}>
                <CheckIcon size={16} />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="hero-visual">
          <div className="xray-frame">
            <XRayArt label={t.hero.artLabel} />
          </div>
          <div className="float-chip chip-a">
            <span className="chip-dot" style={{ background: '#ff7a45' }} />
            <strong>{t.hero.artChips[0].label}</strong>
            <small>{t.hero.artChips[0].detail}</small>
          </div>
          <div className="float-chip chip-b">
            <span className="chip-dot" style={{ background: '#a78bfa' }} />
            <strong>{t.hero.artChips[1].label}</strong>
            <small>{t.hero.artChips[1].detail}</small>
          </div>
        </div>
      </div>
    </section>
  )
}
