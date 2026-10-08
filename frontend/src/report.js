const REPORT_WIDTH = 1600

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = reject
    image.src = src
  })
}

function roundRect(context, x, y, width, height, radius) {
  context.beginPath()
  context.moveTo(x + radius, y)
  context.arcTo(x + width, y, x + width, y + height, radius)
  context.arcTo(x + width, y + height, x, y + height, radius)
  context.arcTo(x, y + height, x, y, radius)
  context.arcTo(x, y, x + width, y, radius)
  context.closePath()
}

// Detections are expressed in the pixel space of the image that was sent to the API (`src`).
export async function renderAnnotatedImage({ src, detections, labelOf, colorOf, footerText, rtl }) {
  const image = await loadImage(src)
  const scale = REPORT_WIDTH / image.naturalWidth
  const width = REPORT_WIDTH
  const imageHeight = Math.round(image.naturalHeight * scale)
  const footerHeight = 72

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = imageHeight + footerHeight
  const context = canvas.getContext('2d')

  context.drawImage(image, 0, 0, width, imageHeight)

  const fontSize = 22
  const fontFamily = '"Plus Jakarta Sans", "Tajawal", system-ui, sans-serif'
  context.lineWidth = 4
  context.textBaseline = 'middle'
  context.font = `700 ${fontSize}px ${fontFamily}`

  for (const detection of detections) {
    const [x1, y1, x2, y2] = detection.bbox_xyxy.map((value) => value * scale)
    const color = colorOf(detection.class_name)
    context.strokeStyle = color
    roundRect(context, x1, y1, x2 - x1, y2 - y1, 8)
    context.stroke()

    const label = labelOf(detection.class_name)
    const labelWidth = context.measureText(label).width + 20
    const labelHeight = fontSize + 14
    const labelY = y1 - labelHeight - 4 > 0 ? y1 - labelHeight - 4 : y2 + 4
    context.fillStyle = color
    roundRect(context, x1, labelY, labelWidth, labelHeight, 8)
    context.fill()
    context.fillStyle = '#0b1020'
    context.direction = rtl ? 'rtl' : 'ltr'
    context.textAlign = rtl ? 'right' : 'left'
    context.fillText(label, rtl ? x1 + labelWidth - 10 : x1 + 10, labelY + labelHeight / 2)
  }

  context.fillStyle = '#141a3d'
  context.fillRect(0, imageHeight, width, footerHeight)
  context.fillStyle = '#ffffff'
  context.font = `600 24px ${fontFamily}`
  context.textAlign = 'center'
  context.direction = rtl ? 'rtl' : 'ltr'
  const date = new Date().toLocaleDateString(rtl ? 'ar-MA' : 'fr-MA')
  context.fillText(`${footerText} · ${date}`, width / 2, imageHeight + footerHeight / 2)

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error('toBlob failed'))), 'image/png')
  })
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export async function shareOrDownload(blob, filename, { title, text }) {
  const file = new File([blob], filename, { type: blob.type })
  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title, text })
      return 'shared'
    } catch (error) {
      if (error?.name === 'AbortError') {
        return 'cancelled'
      }
    }
  }
  downloadBlob(blob, filename)
  return 'downloaded'
}
