async function fileToImage(file) {
  const objectUrl = URL.createObjectURL(file)
  try {
    return await new Promise((resolve, reject) => {
      const image = new Image()
      image.onload = () => resolve(image)
      image.onerror = reject
      image.src = objectUrl
    })
  } finally {
    URL.revokeObjectURL(objectUrl)
  }
}

// Resizes the longest side to `imageSize` and applies brightness/contrast.
// The resulting image is what the model sees, so bbox coordinates are in its pixel space.
export async function preprocessImage(file, { imageSize, brightness, contrast }) {
  const image = await fileToImage(file)
  const scale = imageSize / Math.max(image.width, image.height)
  const width = Math.max(1, Math.round(image.width * scale))
  const height = Math.max(1, Math.round(image.height * scale))

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d')
  context.filter = `brightness(${brightness}%) contrast(${contrast}%)`
  context.drawImage(image, 0, 0, width, height)

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.95))
  if (!blob) {
    throw new Error('Unable to encode the image.')
  }

  return { blob, url: canvas.toDataURL('image/jpeg', 0.95), width, height }
}
