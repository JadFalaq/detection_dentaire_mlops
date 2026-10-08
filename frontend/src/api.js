export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
export const MOCK_API = import.meta.env.VITE_MOCK_API === 'true'

const MOCK_LATENCY_MS = Number(import.meta.env.VITE_MOCK_LATENCY_MS || 800)

const MOCK_CLASSES = [
  'CARIES',
  'PERIAPICAL_PATHOLOGY',
  'PERIODONTAL_BONE',
  'IMPACTED_TOOTH',
  'ROOT_PATHOLOGY',
  'TREATED_TOOTH',
  'DEVICE_IMPLANT',
]

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function mockModelInfo() {
  return {
    model_name: 'champion (mock)',
    checkpoint_path: 'models/checkpoints/champion/weights/best.pt',
    checkpoint_exists: true,
    config_path: 'configs/infer.yaml',
  }
}

async function mockPredict(formData) {
  const file = formData.get('file')
  const confThreshold = Number(formData.get('conf_threshold') || 0.25)
  const maxDet = Number(formData.get('max_det') || 300)
  const bitmap = await createImageBitmap(file)
  const { width, height } = bitmap
  bitmap.close()

  const count = Math.min(maxDet, 3 + Math.floor(Math.random() * 6))
  const detections = []
  for (let i = 0; i < count; i += 1) {
    const confidence = confThreshold + Math.random() * (1 - confThreshold)
    const boxWidth = width * (0.04 + Math.random() * 0.08)
    const boxHeight = height * (0.08 + Math.random() * 0.15)
    const x1 = width * 0.15 + Math.random() * (width * 0.7 - boxWidth)
    const y1 = height * 0.25 + Math.random() * (height * 0.5 - boxHeight)
    const classId = Math.floor(Math.random() * MOCK_CLASSES.length)
    detections.push({
      class_id: classId,
      class_name: MOCK_CLASSES[classId],
      confidence,
      bbox_xyxy: [x1, y1, x1 + boxWidth, y1 + boxHeight],
    })
  }

  return {
    model_name: 'champion (mock)',
    checkpoint_path: 'models/checkpoints/champion/weights/best.pt',
    image_name: file.name,
    num_detections: detections.length,
    image_width: width,
    image_height: height,
    settings: {
      image_size: Number(formData.get('image_size')),
      conf_threshold: confThreshold,
      iou_threshold: Number(formData.get('iou_threshold')),
      max_det: maxDet,
    },
    detections,
  }
}

async function mockFetch(path, options = {}) {
  await wait(MOCK_LATENCY_MS)
  if (path === '/model-info') {
    return jsonResponse(mockModelInfo())
  }
  if (path === '/health') {
    return jsonResponse({ status: 'ok', ...mockModelInfo() })
  }
  if (path === '/predict' && options.method === 'POST') {
    return jsonResponse(await mockPredict(options.body))
  }
  return jsonResponse({ detail: 'Not Found' }, 404)
}

export function apiFetch(path, options) {
  if (MOCK_API) {
    return mockFetch(path, options)
  }
  return fetch(`${API_BASE_URL}${path}`, options)
}
