import { useI18n } from '../i18n/context'
import { GlobeIcon, ToothIcon } from './Icons'

export function StatusPill({ status }) {
  const { t } = useI18n()
  return (
    <span className={`status-pill status-${status}`} role="status">
      <span className="status-dot" aria-hidden="true" />
      {t.status[status]}
    </span>
  )
}

export function Logo() {
  return (
    <a href="#top" className="logo" aria-label="Snani">
      <span className="logo-mark">
        <ToothIcon size={22} />
      </span>
      <span className="logo-text">
        <strong>Snani</strong>
        <span lang="ar">سناني</span>
      </span>
    </a>
  )
}

export default function Header({ status }) {
  const { t, toggleLang } = useI18n()
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Logo />
        <nav className="main-nav" aria-label="Navigation">
          <a href="#comment">{t.nav.how}</a>
          <a href="#guide">{t.nav.guide}</a>
          <a href="#ia">{t.nav.ai}</a>
          <a href="#faq">{t.nav.faq}</a>
        </nav>
        <div className="header-actions">
          <StatusPill status={status} />
          <button type="button" className="lang-btn" onClick={toggleLang} aria-label={t.langSwitchLabel}>
            <GlobeIcon size={16} />
            <span>{t.langSwitch}</span>
          </button>
          <a href="#analyse" className="btn btn-primary btn-sm header-cta">
            {t.nav.cta}
          </a>
        </div>
      </div>
    </header>
  )
}
