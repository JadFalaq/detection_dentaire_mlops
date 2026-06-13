import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const DEFAULT_CONTROLS = {
  imageSize: 896,
  confThreshold: 0.25,
  iouThreshold: 0.5,
  maxDet: 300,
  brightness: 100,
  contrast: 100,
}

const INITIAL_MODEL_INFO = {
  model_name: 'champion',
  checkpoint_exists: false,
}

function formatConfidence(value) {
  return `${Math.round(value * 100)}%`
}

function sortDetections(detections) {
  return [...detections].sort((left, right) => right.confidence - left.confidence)
}

async function fileToImage(file) {
  const objectUrl = URL.createObjectURL(file)
  try {
    const image = await new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = objectUrl
    })
    return image
  } finally {
    URL.revokeObjectURL(objectUrl)
  }
}

async function preprocessImage(file, controls) {
  const image = await fileToImage(file)
  const longestSide = Math.max(image.width, image.height)
  const scale = controls.imageSize / longestSide
  const targetWidth = Math.max(1, Math.round(image.width * scale))
  const targetHeight = Math.max(1, Math.round(image.height * scale))

  const canvas = document.createElement('canvas')
  canvas.width = targetWidth
  canvas.height = targetHeight

  const context = canvas.getContext('2d')
  if (!context) {
    throw new Error('Impossible d initialiser le canvas de preprocessing.')
  }
  context.filter = `brightness(${controls.brightness}%) contrast(${controls.contrast}%)`
  context.drawImage(image, 0, 0, targetWidth, targetHeight)

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.96))
  if (!blob) {
    throw new Error('Impossible de generer l image preprocessée.')
  }
  const previewUrl = canvas.toDataURL('image/jpeg', 0.96)

  return {
    blob,
    previewUrl,
    originalWidth: image.width,
    originalHeight: image.height,
    width: targetWidth,
    height: targetHeight,
    scale,
  }
}

function App() {
  const fileInputRef = useRef(null)
  const [modelInfo, setModelInfo] = useState(INITIAL_MODEL_INFO)
  const [selectedFile, setSelectedFile] = useState(null)
  const [processedPreview, setProcessedPreview] = useState(null)
  const [processedBlob, setProcessedBlob] = useState(null)
  const [originalDimensions, setOriginalDimensions] = useState({ width: 0, height: 0 })
  const [processedDimensions, setProcessedDimensions] = useState({ width: 0, height: 0 })
  const [preprocessScale, setPreprocessScale] = useState(null)
  const [controls, setControls] = useState(DEFAULT_CONTROLS)
  const [detections, setDetections] = useState([])
  const [serverMeta, setServerMeta] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)

  useEffect(() => {
    async function loadModelInfo() {
      try {
        const response = await fetch(`${API_BASE_URL}/model-info`)
        if (!response.ok) {
          throw new Error('Impossible de recuperer les informations du modele.')
        }
        const payload = await response.json()
        setModelInfo(payload)
      } catch (err) {
        setError(err.message)
      }
    }

    loadModelInfo()
  }, [])

  const detectionSummary = useMemo(() => {
    const counter = new Map()
    for (const detection of detections) {
      counter.set(detection.class_name, (counter.get(detection.class_name) || 0) + 1)
    }
    return Array.from(counter.entries()).map(([label, count]) => ({ label, count }))
  }, [detections])

  async function updateProcessedPreview(file, nextControls) {
    if (!file) {
      return
    }

    const processed = await preprocessImage(file, nextControls)
    setProcessedBlob(processed.blob)
    setProcessedPreview(processed.previewUrl)
    setOriginalDimensions({
      width: processed.originalWidth,
      height: processed.originalHeight,
    })
    setProcessedDimensions({ width: processed.width, height: processed.height })
    setPreprocessScale(processed.scale)
    setDetections([])
    setServerMeta(null)
  }

  async function handleFile(file) {
    if (!file) {
      return
    }

    setError('')
    setSelectedFile(file)
    await updateProcessedPreview(file, controls)
  }

  async function handleControlChange(key, value) {
    const nextControls = { ...controls, [key]: value }
    setControls(nextControls)

    if (selectedFile && ['imageSize', 'brightness', 'contrast'].includes(key)) {
      await updateProcessedPreview(selectedFile, nextControls)
    }
  }

  async function handleAnalyze() {
    if (!selectedFile || !processedBlob) {
      setError('Charge d abord une radiographie avant de lancer l analyse.')
      return
    }

    setIsProcessing(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append(
        'file',
        new File([processedBlob], `processed-${selectedFile.name}`, { type: 'image/jpeg' }),
      )
      formData.append('image_size', String(controls.imageSize))
      formData.append('conf_threshold', String(controls.confThreshold))
      formData.append('iou_threshold', String(controls.iouThreshold))
      formData.append('max_det', String(controls.maxDet))

      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Le service d inference a renvoye une erreur.')
      }

      const payload = await response.json()
      setDetections(sortDetections(payload.detections || []))
      setServerMeta(payload)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsProcessing(false)
    }
  }

  function handleReset() {
    setSelectedFile(null)
    setProcessedPreview(null)
    setProcessedBlob(null)
    setOriginalDimensions({ width: 0, height: 0 })
    setProcessedDimensions({ width: 0, height: 0 })
    setPreprocessScale(null)
    setDetections([])
    setServerMeta(null)
    setError('')
    setControls(DEFAULT_CONTROLS)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  function openFileDialog() {
    fileInputRef.current?.click()
  }

  return (
    <div className="app-shell">
      <header className="hero-panel">
        <div>
          <span className="eyebrow">Dental AI Agent</span>
          <h1>Analyse intelligente de radiographies panoramiques dentaires</h1>
          <p className="hero-copy">
            Upload une radio, ajuste les controles d analyse et laisse le modele
            Champion detecter les anomalies dentaires avec un rendu visuel des bbox
            directement sur l image.
          </p>
        </div>
        <div className="hero-stats">
          <div className="stat-card">
            <span>Modele actif</span>
            <strong>{modelInfo.model_name || 'champion'}</strong>
          </div>
          <div className="stat-card">
            <span>Checkpoint</span>
            <strong>{modelInfo.checkpoint_exists ? 'Disponible' : 'Absent'}</strong>
          </div>
          <div className="stat-card">
            <span>API</span>
            <strong>{API_BASE_URL}</strong>
          </div>
        </div>
      </header>

      <main className="workspace-grid">
        <section className="panel controls-panel">
          <div className="panel-header">
            <h2>Upload et controles</h2>
            <p>Prepare la radio puis configure l analyse du modele.</p>
          </div>

          <button
            type="button"
            className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
            onClick={openFileDialog}
            onDragOver={(event) => {
              event.preventDefault()
              setDragActive(true)
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={async (event) => {
              event.preventDefault()
              setDragActive(false)
              await handleFile(event.dataTransfer.files?.[0])
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              hidden
              onChange={async (event) => handleFile(event.target.files?.[0])}
            />
            <span className="upload-icon">+</span>
            <strong>Glisse ta radiographie ici ou clique pour uploader</strong>
            <small>
              Formats acceptes: JPG, PNG, BMP, TIFF, WEBP. Le site reconstruit une
              image preprocessée avant de l envoyer au modele.
            </small>
          </button>

          <div className="control-group">
            <label>
              Taille cible d analyse
              <select
                value={controls.imageSize}
                onChange={(event) => handleControlChange('imageSize', Number(event.target.value))}
              >
                <option value={640}>640 px</option>
                <option value={896}>896 px</option>
                <option value={1024}>1024 px</option>
              </select>
            </label>

            <label>
              Confiance minimale
              <span>{controls.confThreshold.toFixed(2)}</span>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.01"
                value={controls.confThreshold}
                onChange={(event) =>
                  handleControlChange('confThreshold', Number(event.target.value))
                }
              />
            </label>

            <label>
              Seuil IoU
              <span>{controls.iouThreshold.toFixed(2)}</span>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.01"
                value={controls.iouThreshold}
                onChange={(event) => handleControlChange('iouThreshold', Number(event.target.value))}
              />
            </label>

            <label>
              Nombre max de detections
              <input
                type="number"
                min="1"
                max="500"
                value={controls.maxDet}
                onChange={(event) => handleControlChange('maxDet', Number(event.target.value))}
              />
            </label>
          </div>

          <div className="control-group">
            <label>
              Luminosite preprocessing
              <span>{controls.brightness}%</span>
              <input
                type="range"
                min="70"
                max="140"
                step="1"
                value={controls.brightness}
                onChange={(event) => handleControlChange('brightness', Number(event.target.value))}
              />
            </label>

            <label>
              Contraste preprocessing
              <span>{controls.contrast}%</span>
              <input
                type="range"
                min="80"
                max="170"
                step="1"
                value={controls.contrast}
                onChange={(event) => handleControlChange('contrast', Number(event.target.value))}
              />
            </label>
          </div>

          <div className="action-row">
            <button type="button" className="primary-btn" onClick={handleAnalyze} disabled={isProcessing}>
              {isProcessing ? 'Analyse en cours...' : 'Lancer l analyse'}
            </button>
            <button type="button" className="ghost-btn" onClick={handleReset}>
              Reinitialiser
            </button>
          </div>

          {error ? <p className="error-banner">{error}</p> : null}
          {selectedFile ? (
            <div className="file-meta">
              <span>Fichier selectionne</span>
              <strong>{selectedFile.name}</strong>
              {originalDimensions.width > 0 ? (
                <small>
                  Originale: {originalDimensions.width} x {originalDimensions.height} {'->'} preprocessee:{' '}
                  {processedDimensions.width} x {processedDimensions.height}
                </small>
              ) : null}
            </div>
          ) : null}
        </section>

        <section className="panel visual-panel">
          <div className="panel-header">
            <h2>Rendu visuel avec bbox</h2>
            <p>La radio preprocessée est celle qui est envoyee au modele Champion.</p>
          </div>

          {processedPreview ? (
            <div className="preview-stage">
              <div className="image-frame">
                <img
                  src={processedPreview}
                  alt="Radiographie preprocessée"
                  className="preview-image"
                />
                {detections.map((detection, index) => {
                  const [x1, y1, x2, y2] = detection.bbox_xyxy
                  const width = processedDimensions.width || serverMeta?.image_width || 1
                  const height = processedDimensions.height || serverMeta?.image_height || 1
                  return (
                    <div
                      key={`${detection.class_name}-${index}`}
                      className="bbox"
                      style={{
                        left: `${(x1 / width) * 100}%`,
                        top: `${(y1 / height) * 100}%`,
                        width: `${((x2 - x1) / width) * 100}%`,
                        height: `${((y2 - y1) / height) * 100}%`,
                      }}
                    >
                      <span>
                        {detection.class_name} · {formatConfidence(detection.confidence)}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <h3>Aucune image chargee</h3>
              <p>Upload une radiographie pour visualiser la zone d analyse et les futures bbox.</p>
            </div>
          )}
        </section>

        <section className="panel insights-panel">
          <div className="panel-header">
            <h2>Predictions et synthese</h2>
            <p>Lecture rapide des detections renvoyees par le modele.</p>
          </div>

          <div className="summary-strip">
            <div className="mini-card">
              <span>Detections</span>
              <strong>{detections.length}</strong>
            </div>
            <div className="mini-card">
              <span>Resolution envoyee</span>
              <strong>
                {processedDimensions.width > 0
                  ? `${processedDimensions.width} x ${processedDimensions.height}`
                  : '-'}
              </strong>
            </div>
            <div className="mini-card">
              <span>Reshape applique</span>
              <strong>{preprocessScale ? `x${preprocessScale.toFixed(2)}` : '-'}</strong>
            </div>
            <div className="mini-card">
              <span>Reglage confiance</span>
              <strong>{controls.confThreshold.toFixed(2)}</strong>
            </div>
          </div>

          <div className="prediction-layout">
            <div className="prediction-panel">
              <h3>Repartition par classe</h3>
              {detectionSummary.length > 0 ? (
                <ul className="summary-list">
                  {detectionSummary.map((item) => (
                    <li key={item.label}>
                      <span>{item.label}</span>
                      <strong>{item.count}</strong>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  Les classes detectees apparaitront ici apres l inference.
                </p>
              )}
            </div>

            <div className="prediction-panel">
              <h3>Liste detaillee</h3>
              {detections.length > 0 ? (
                <ul className="detection-list">
                  {detections.map((detection, index) => (
                    <li key={`${detection.class_name}-${index}`}>
                      <div>
                        <strong>{detection.class_name}</strong>
                        <span>{formatConfidence(detection.confidence)}</span>
                      </div>
                      <code>
                        {detection.bbox_xyxy.map((value) => Math.round(value)).join(', ')}
                      </code>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">
                  Aucune detection pour le moment. Lance l analyse pour voir les predictions.
                </p>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
