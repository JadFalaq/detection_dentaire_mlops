import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { apiFetch } from '../api'
import { EXAMPLE_EVENT } from '../events'
import { useI18n } from '../i18n/context'
import { preprocessImage } from '../imaging'
import {
  CameraIcon,
  CheckIcon,
  ChevronIcon,
  RefreshIcon,
  ShieldIcon,
  SparkIcon,
  UploadIcon,
} from './Icons'
import ImageStage from './ImageStage'
import ResultsPanel from './ResultsPanel'
import SectionHead from './SectionHead'

const QUALITY_SIZES = { fast: 640, standard: 832, detailed: 1024 }
const SENSITIVITY_THRESHOLDS = { careful: 0.4, balanced: 0.25, sensitive: 0.15 }
// Ask the API for everything above the lowest threshold, then filter locally so the
// sensitivity can change instantly after an analysis.
const REQUEST_CONFIDENCE = Math.min(...Object.values(SENSITIVITY_THRESHOLDS))
const DEFAULT_SETTINGS = { quality: 'standard', sensitivity: 'balanced', brightness: 100, contrast: 100 }
const EXAMPLE_URL = '/exemple-radio.jpg'

function Segmented({ label, value, options, onChange }) {
  return (
    <div className="segmented-field">
      <span className="field-label">{label}</span>
      <div className="segmented" role="radiogroup" aria-label={label}>
        {Object.entries(options).map(([key, text]) => (
          <button
            key={key}
            type="button"
            role="radio"
            aria-checked={value === key}
            className={value === key ? 'is-selected' : ''}
            onClick={() => onChange(key)}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function Analyzer({ status, onWake, onServerActive }) {
  const { t } = useI18n()
  const copy = t.analyzer
  const fileInputRef = useRef(null)
  const cameraInputRef = useRef(null)
  const sideRef = useRef(null)
  const stepTimerRef = useRef(null)

  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [settings, setSettings] = useState(DEFAULT_SETTINGS)
  const [phase, setPhase] = useState('empty')
  const [errorKey, setErrorKey] = useState('')
  const [rawDetections, setRawDetections] = useState([])
  const [activeClass, setActiveClass] = useState(null)
  const [hiddenClasses, setHiddenClasses] = useState(() => new Set())
  const [step, setStep] = useState(0)
  const [dragActive, setDragActive] = useState(false)
  const [loadingExample, setLoadingExample] = useState(false)

  const threshold = SENSITIVITY_THRESHOLDS[settings.sensitivity]
  const detections = rawDetections.filter((detection) => detection.confidence >= threshold)
  const serverSlow = status === 'sleeping' || status === 'checking' || status === 'waking'

  useEffect(() => () => clearInterval(stepTimerRef.current), [])

  async function preparePreview(nextFile, nextSettings) {
    const processed = await preprocessImage(nextFile, {
      imageSize: QUALITY_SIZES[nextSettings.quality],
      brightness: nextSettings.brightness,
      contrast: nextSettings.contrast,
    })
    setPreview(processed)
    setRawDetections([])
    setActiveClass(null)
    setHiddenClasses(new Set())
    setErrorKey('')
    setPhase('ready')
  }

  async function handleFile(nextFile) {
    if (!nextFile) return
    if (!nextFile.type.startsWith('image/')) {
      setErrorKey('wrongType')
      return
    }
    try {
      setFile(nextFile)
      await preparePreview(nextFile, settings)
      onWake()
    } catch {
      setFile(null)
      setPhase('empty')
      setErrorKey('wrongType')
    }
  }

  async function updateSetting(key, value) {
    const next = { ...settings, [key]: value }
    setSettings(next)
    if (file && key !== 'sensitivity') {
      await preparePreview(file, next)
    }
  }

  async function resetImageSettings() {
    const next = { ...settings, brightness: 100, contrast: 100 }
    setSettings(next)
    if (file) await preparePreview(file, next)
  }

  async function loadExample() {
    setLoadingExample(true)
    try {
      const response = await fetch(EXAMPLE_URL)
      const blob = await response.blob()
      await handleFile(new File([blob], 'exemple-radio.jpg', { type: blob.type || 'image/jpeg' }))
    } catch {
      setErrorKey('wrongType')
    } finally {
      setLoadingExample(false)
    }
  }

  const onExampleRequested = useEffectEvent(() => {
    loadExample()
  })

  useEffect(() => {
    const handler = () => onExampleRequested()
    window.addEventListener(EXAMPLE_EVENT, handler)
    return () => window.removeEventListener(EXAMPLE_EVENT, handler)
  }, [])

  async function analyze() {
    if (!preview) return
    onWake()
    setPhase('analyzing')
    setErrorKey('')
    setStep(0)
    setActiveClass(null)
    clearInterval(stepTimerRef.current)
    stepTimerRef.current = setInterval(() => setStep((value) => Math.min(value + 1, copy.steps.length - 1)), 1400)

    try {
      const formData = new FormData()
      formData.append('file', new File([preview.blob], 'radio.jpg', { type: 'image/jpeg' }))
      formData.append('image_size', String(QUALITY_SIZES[settings.quality]))
      formData.append('conf_threshold', String(REQUEST_CONFIDENCE))
      formData.append('iou_threshold', '0.5')
      formData.append('max_det', '100')

      const response = await apiFetch('/predict', {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(150000),
      })
      if (!response.ok) {
        setErrorKey(response.status === 429 ? 'rateLimited' : response.status === 413 ? 'tooLarge' : 'server')
        setPhase('error')
        return
      }
      onServerActive()
      const payload = await response.json()
      setRawDetections([...(payload.detections || [])].sort((left, right) => right.confidence - left.confidence))
      setHiddenClasses(new Set())
      setPhase('done')
      if (window.matchMedia('(max-width: 900px)').matches) {
        requestAnimationFrame(() => sideRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
      }
    } catch {
      setErrorKey('network')
      setPhase('error')
    } finally {
      clearInterval(stepTimerRef.current)
    }
  }

  function reset() {
    setFile(null)
    setPreview(null)
    setRawDetections([])
    setActiveClass(null)
    setHiddenClasses(new Set())
    setErrorKey('')
    setPhase('empty')
    setSettings((current) => ({ ...DEFAULT_SETTINGS, sensitivity: current.sensitivity }))
    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
    document.getElementById('analyse')?.scrollIntoView({ behavior: 'smooth' })
  }

  function toggleClass(id) {
    setHiddenClasses((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const statusNote =
    status === 'offline' ? (
      <div className="note note-warn">
        <p>{copy.offlineNote}</p>
        <button type="button" className="btn btn-link btn-sm" onClick={onWake}>
          <RefreshIcon size={16} />
          {copy.retryConnection}
        </button>
      </div>
    ) : serverSlow ? (
      <div className="note note-info">
        <SparkIcon size={18} className="spin-slow" />
        <p>{copy.wakingNote}</p>
      </div>
    ) : null

  return (
    <section className="section analyzer-section" id="analyse">
      <div className="container">
        <SectionHead eyebrow={copy.eyebrow} title={copy.title} lead={copy.lead} center />

        <div className="analyzer-card">
          {phase === 'empty' ? (
            <div className="drop-layout">
              <div
                className={`dropzone ${dragActive ? 'is-drag' : ''}`}
                onDragOver={(event) => {
                  event.preventDefault()
                  setDragActive(true)
                }}
                onDragLeave={() => setDragActive(false)}
                onDrop={(event) => {
                  event.preventDefault()
                  setDragActive(false)
                  handleFile(event.dataTransfer.files?.[0])
                }}
              >
                <div className="dropzone-icon">
                  <UploadIcon size={30} />
                </div>
                <h3>{copy.dropTitle}</h3>
                <p className="muted">{copy.dropHint}</p>
                <div className="dropzone-buttons">
                  <button type="button" className="btn btn-primary" onClick={() => fileInputRef.current?.click()}>
                    <UploadIcon size={18} />
                    {copy.choose}
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost camera-btn"
                    onClick={() => cameraInputRef.current?.click()}
                  >
                    <CameraIcon size={18} />
                    {copy.camera}
                  </button>
                </div>
                <button type="button" className="btn btn-link" onClick={loadExample} disabled={loadingExample}>
                  {loadingExample ? copy.exampleLoading : copy.example}
                </button>
                {errorKey === 'wrongType' ? <p className="inline-error">{copy.wrongType}</p> : null}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={(event) => handleFile(event.target.files?.[0])}
                />
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  hidden
                  onChange={(event) => handleFile(event.target.files?.[0])}
                />
              </div>

              <aside className="drop-aside">
                <details className="tips" open>
                  <summary>
                    <CameraIcon size={18} />
                    <span>{copy.tipsTitle}</span>
                    <ChevronIcon size={18} className="chevron" />
                  </summary>
                  <ol>
                    {copy.tips.map((tip) => (
                      <li key={tip}>{tip}</li>
                    ))}
                  </ol>
                </details>
                <p className="privacy">
                  <ShieldIcon size={20} />
                  {copy.privacy}
                </p>
              </aside>
            </div>
          ) : (
            <div className="workspace">
              <div className="workspace-visual">
                {preview ? (
                  <ImageStage
                    preview={preview}
                    detections={phase === 'done' ? detections : []}
                    activeClass={activeClass}
                    hiddenClasses={hiddenClasses}
                    analyzing={phase === 'analyzing'}
                  />
                ) : null}
              </div>

              <div className="workspace-side" ref={sideRef}>
                {phase === 'ready' || phase === 'error' ? (
                  <div className="ready-panel">
                    <div className="file-chip">
                      <span>{copy.fileLabel}</span>
                      <strong>{file?.name}</strong>
                    </div>
                    {statusNote}
                    {phase === 'error' ? <p className="inline-error">{copy.errors[errorKey]}</p> : null}
                    <button type="button" className="btn btn-primary btn-lg btn-block" onClick={analyze}>
                      <SparkIcon size={20} />
                      {phase === 'error' ? copy.retry : copy.analyze}
                    </button>

                    <details className="advanced">
                      <summary>
                        <span>{copy.advanced}</span>
                        <ChevronIcon size={18} className="chevron" />
                      </summary>
                      <div className="advanced-body">
                        <Segmented
                          label={copy.quality}
                          value={settings.quality}
                          options={copy.qualityOptions}
                          onChange={(value) => updateSetting('quality', value)}
                        />
                        <Segmented
                          label={copy.sensitivity}
                          value={settings.sensitivity}
                          options={copy.sensitivityOptions}
                          onChange={(value) => updateSetting('sensitivity', value)}
                        />
                        <p className="field-help">{copy.sensitivityHelp[settings.sensitivity]}</p>
                        <label className="slider-field">
                          <span className="field-label">
                            {copy.brightness} <output>{settings.brightness}%</output>
                          </span>
                          <input
                            type="range"
                            min="70"
                            max="140"
                            value={settings.brightness}
                            onChange={(event) => updateSetting('brightness', Number(event.target.value))}
                          />
                        </label>
                        <label className="slider-field">
                          <span className="field-label">
                            {copy.contrast} <output>{settings.contrast}%</output>
                          </span>
                          <input
                            type="range"
                            min="80"
                            max="170"
                            value={settings.contrast}
                            onChange={(event) => updateSetting('contrast', Number(event.target.value))}
                          />
                        </label>
                        <button type="button" className="btn btn-link btn-sm" onClick={resetImageSettings}>
                          {copy.resetImage}
                        </button>
                      </div>
                    </details>

                    <button type="button" className="btn btn-link" onClick={reset}>
                      <RefreshIcon size={16} />
                      {copy.change}
                    </button>
                  </div>
                ) : null}

                {phase === 'analyzing' ? (
                  <div className="progress-panel" aria-live="polite">
                    <ol className="progress-steps">
                      {copy.steps.map((label, index) => (
                        <li key={label} className={index < step ? 'is-done' : index === step ? 'is-current' : ''}>
                          <span className="step-bullet">{index < step ? <CheckIcon size={14} /> : index + 1}</span>
                          {label}
                        </li>
                      ))}
                    </ol>
                    {statusNote}
                  </div>
                ) : null}

                {phase === 'done' ? (
                  <>
                    <Segmented
                      label={copy.sensitivity}
                      value={settings.sensitivity}
                      options={copy.sensitivityOptions}
                      onChange={(value) => updateSetting('sensitivity', value)}
                    />
                    <ResultsPanel
                      detections={detections}
                      preview={preview}
                      activeClass={activeClass}
                      onSelectClass={setActiveClass}
                      hiddenClasses={hiddenClasses}
                      onToggleClass={toggleClass}
                      onReset={reset}
                    />
                  </>
                ) : null}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
