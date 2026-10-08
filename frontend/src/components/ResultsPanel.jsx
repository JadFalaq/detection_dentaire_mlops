import { useState } from 'react'
import { MOCK_API } from '../api'
import { URGENCY_RANK, getCondition } from '../content/conditions'
import { useI18n } from '../i18n/context'
import { downloadBlob, renderAnnotatedImage, shareOrDownload } from '../report'
import {
  AlertIcon,
  CalendarIcon,
  CheckIcon,
  DownloadIcon,
  MapPinIcon,
  RefreshIcon,
  SendIcon,
  SmileIcon,
  WhatsappIcon,
} from './Icons'

const VERDICT_ICONS = { high: AlertIcon, medium: CalendarIcon, low: CheckIcon, none: SmileIcon }

function certaintyLevel(confidence) {
  if (confidence >= 0.6) return 'high'
  if (confidence >= 0.35) return 'medium'
  return 'low'
}

function groupDetections(detections) {
  const groups = new Map()
  for (const detection of detections) {
    const group = groups.get(detection.class_name) || { id: detection.class_name, count: 0, maxConfidence: 0 }
    group.count += 1
    group.maxConfidence = Math.max(group.maxConfidence, detection.confidence)
    groups.set(detection.class_name, group)
  }
  return [...groups.values()]
    .map((group) => {
      const condition = getCondition(group.id)
      const uncertain = certaintyLevel(group.maxConfidence) === 'low'
      // A single low-certainty sign should not trigger the most alarming verdict.
      const verdictUrgency = condition.urgency === 'high' && uncertain ? 'medium' : condition.urgency
      return { ...group, condition, verdictUrgency }
    })
    .sort(
      (left, right) =>
        URGENCY_RANK[right.verdictUrgency] - URGENCY_RANK[left.verdictUrgency] || right.count - left.count,
    )
}

function verdictFor(groups) {
  if (groups.length === 0) return 'none'
  const top = groups[0].verdictUrgency
  if (top === 'high') return 'high'
  if (top === 'medium') return 'medium'
  return 'low'
}

export default function ResultsPanel({
  detections,
  preview,
  activeClass,
  onSelectClass,
  hiddenClasses,
  onToggleClass,
  onReset,
}) {
  const { t, lang } = useI18n()
  const [busy, setBusy] = useState('')
  const groups = groupDetections(detections)
  const verdict = verdictFor(groups)
  const VerdictIcon = VERDICT_ICONS[verdict]

  async function buildReport() {
    return renderAnnotatedImage({
      src: preview.url,
      detections: detections.filter((detection) => !hiddenClasses.has(detection.class_name)),
      labelOf: (id) => getCondition(id)[lang].name,
      colorOf: (id) => getCondition(id).color,
      footerText: t.results.reportFooter,
      rtl: lang === 'ar',
    })
  }

  async function handleDownload() {
    setBusy('download')
    try {
      downloadBlob(await buildReport(), 'snani-radio-analysee.png')
    } finally {
      setBusy('')
    }
  }

  async function handleShare() {
    setBusy('share')
    try {
      await shareOrDownload(await buildReport(), 'snani-radio-analysee.png', {
        title: t.results.shareTitle,
        text: t.results.shareText,
      })
    } finally {
      setBusy('')
    }
  }

  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(`${t.results.whatsappText} ${window.location.origin}`)}`
  const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(lang === 'ar' ? 'طبيب أسنان' : 'dentiste')}`

  return (
    <div className="results">
      {MOCK_API ? <p className="demo-notice">{t.results.demoNotice}</p> : null}

      <div className={`verdict verdict-${verdict}`}>
        <span className="verdict-icon">
          <VerdictIcon size={26} />
        </span>
        <div>
          <span className="verdict-count">{t.results.found(detections.length)}</span>
          <h3>{t.results.verdicts[verdict].title}</h3>
          <p>{t.results.verdicts[verdict].text}</p>
        </div>
      </div>

      {groups.length > 0 ? (
        <>
          <p className="hint">{t.results.tapHint}</p>
          <ul className="finding-list">
            {groups.map((group) => {
              const copy = group.condition[lang]
              const isActive = activeClass === group.id
              const isHidden = hiddenClasses.has(group.id)
              return (
                <li key={group.id} className={`finding ${isActive ? 'is-active' : ''}`} style={{ '--c': group.condition.color }}>
                  <button
                    type="button"
                    className="finding-head"
                    aria-expanded={isActive}
                    onClick={() => onSelectClass(isActive ? null : group.id)}
                  >
                    <span className="finding-swatch" />
                    <span className="finding-title">
                      <strong>
                        {copy.name} <span className="finding-count">{t.results.times(group.count)}</span>
                      </strong>
                      <small>
                        {t.results.certainty[certaintyLevel(group.maxConfidence)]}
                      </small>
                    </span>
                    <span className={`urgency-badge urgency-${group.condition.urgency}`}>
                      {t.results.urgency[group.condition.urgency]}
                    </span>
                  </button>
                  {isActive ? (
                    <div className="finding-body">
                      <p>{copy.explain}</p>
                      <p className="finding-advice">
                        <strong>{t.results.whatToDo}</strong> {copy.advice}
                      </p>
                    </div>
                  ) : null}
                  <button
                    type="button"
                    className={`eye-toggle ${isHidden ? 'is-off' : ''}`}
                    onClick={() => onToggleClass(group.id)}
                    aria-pressed={!isHidden}
                    title={t.results.legendHint}
                    aria-label={`${t.results.legendHint} : ${copy.name}`}
                  >
                    <span />
                  </button>
                </li>
              )
            })}
          </ul>
        </>
      ) : null}

      <div className="result-actions">
        {groups.length > 0 ? (
          <>
            <button type="button" className="btn btn-primary" onClick={handleShare} disabled={Boolean(busy)}>
              <SendIcon size={18} />
              {t.results.share}
            </button>
            <button type="button" className="btn btn-ghost" onClick={handleDownload} disabled={Boolean(busy)}>
              <DownloadIcon size={18} />
              {t.results.download}
            </button>
          </>
        ) : null}
        <a className="btn btn-ghost" href={mapsUrl} target="_blank" rel="noreferrer">
          <MapPinIcon size={18} />
          {t.results.findDentist}
        </a>
        <a className="btn btn-whatsapp" href={whatsappUrl} target="_blank" rel="noreferrer">
          <WhatsappIcon size={18} />
          {t.results.whatsapp}
        </a>
        <button type="button" className="btn btn-link" onClick={onReset}>
          <RefreshIcon size={18} />
          {t.results.another}
        </button>
      </div>

      <p className="disclaimer">{t.results.disclaimer}</p>
    </div>
  )
}
