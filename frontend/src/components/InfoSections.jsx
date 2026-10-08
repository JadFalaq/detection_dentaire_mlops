import { useState } from 'react'
import { CONDITIONS } from '../content/conditions'
import { useI18n } from '../i18n/context'
import { CameraIcon, ChevronIcon, SparkIcon, ToothIcon, UploadIcon } from './Icons'
import { Logo } from './Header'
import SectionHead from './SectionHead'

const STEP_ICONS = [CameraIcon, UploadIcon, SparkIcon]

export function HowItWorks() {
  const { t } = useI18n()
  return (
    <section className="section" id="comment">
      <div className="container">
        <SectionHead eyebrow={t.how.eyebrow} title={t.how.title} center />
        <ol className="steps-grid">
          {t.how.steps.map((step, index) => {
            const Icon = STEP_ICONS[index]
            return (
              <li key={step.title} className="step-card">
                <span className="step-number">{index + 1}</span>
                <span className="step-icon">
                  <Icon size={26} />
                </span>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </li>
            )
          })}
        </ol>
      </div>
    </section>
  )
}

export function ConditionsGuide() {
  const { t, lang } = useI18n()
  const [openId, setOpenId] = useState(CONDITIONS[1].id)
  return (
    <section className="section section-tinted" id="guide">
      <div className="container">
        <SectionHead eyebrow={t.guide.eyebrow} title={t.guide.title} lead={t.guide.lead} center />
        <div className="guide-grid">
          {CONDITIONS.map((condition) => {
            const copy = condition[lang]
            const isOpen = openId === condition.id
            return (
              <article
                key={condition.id}
                className={`guide-card ${isOpen ? 'is-open' : ''}`}
                style={{ '--c': condition.color }}
              >
                <button
                  type="button"
                  className="guide-head"
                  aria-expanded={isOpen}
                  onClick={() => setOpenId(isOpen ? null : condition.id)}
                >
                  <span className="guide-icon">
                    <ToothIcon size={22} />
                  </span>
                  <span className="guide-title">
                    <strong>{copy.name}</strong>
                    <small>{copy.short}</small>
                  </span>
                  <span className={`urgency-badge urgency-${condition.urgency}`}>
                    {t.results.urgency[condition.urgency]}
                  </span>
                  <ChevronIcon size={20} className="chevron" />
                </button>
                {isOpen ? (
                  <div className="guide-body">
                    <p>{copy.explain}</p>
                    <p className="finding-advice">
                      <strong>{t.results.whatToDo}</strong> {copy.advice}
                    </p>
                  </div>
                ) : null}
              </article>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export function AiExplained() {
  const { t } = useI18n()
  return (
    <section className="section" id="ia">
      <div className="container ai-grid">
        <div>
          <SectionHead eyebrow={t.ai.eyebrow} title={t.ai.title} />
          {t.ai.paragraphs.map((paragraph) => (
            <p key={paragraph} className="body-text">
              {paragraph}
            </p>
          ))}
          <dl className="stats-row">
            {t.ai.stats.map((stat) => (
              <div key={stat.label} className="stat">
                <dt>{stat.label}</dt>
                <dd>{stat.value}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="honesty-card">
          <h3>{t.ai.honestyTitle}</h3>
          {t.ai.meters.map((meter) => (
            <div key={meter.label} className={`meter meter-${meter.tone}`}>
              <div className="meter-text">
                <span>{meter.label}</span>
                <strong>{meter.value}</strong>
              </div>
              <div className="meter-track" aria-hidden="true">
                <span style={{ width: `${meter.ratio * 100}%` }} />
              </div>
            </div>
          ))}
          <p className="honesty-note">{t.ai.honestyNote}</p>
          <p className="source-note">{t.ai.source}</p>
        </div>
      </div>
    </section>
  )
}

export function Faq() {
  const { t } = useI18n()
  return (
    <section className="section section-tinted" id="faq">
      <div className="container narrow">
        <SectionHead eyebrow={t.faq.eyebrow} title={t.faq.title} center />
        <div className="faq-list">
          {t.faq.items.map((item) => (
            <details key={item.q} className="faq-item">
              <summary>
                <span>{item.q}</span>
                <ChevronIcon size={20} className="chevron" />
              </summary>
              <p>{item.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  )
}

export function FinalCta() {
  const { t } = useI18n()
  return (
    <section className="final-cta">
      <div className="container final-inner">
        <h2>{t.final.title}</h2>
        <p>{t.final.text}</p>
        <a href="#analyse" className="btn btn-light btn-lg">
          {t.final.cta}
        </a>
      </div>
    </section>
  )
}

export function Footer() {
  const { t } = useI18n()
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <Logo />
          <p className="footer-tagline">{t.brandTagline}</p>
        </div>
        <div>
          <p className="footer-urgent">{t.footer.urgent}</p>
        </div>
        <div className="footer-links">
          <small>{t.footer.rights}</small>
        </div>
      </div>
    </footer>
  )
}
