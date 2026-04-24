const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const USER_MEDIA_BASE_URL = import.meta.env.VITE_USER_MEDIA_BASE_URL ?? 'http://127.0.0.1:8001'
const RESTAURANT_MEDIA_BASE_URL = import.meta.env.VITE_RESTAURANT_MEDIA_BASE_URL ?? 'http://127.0.0.1:8003'
const REVIEW_MEDIA_BASE_URL = import.meta.env.VITE_REVIEW_MEDIA_BASE_URL ?? 'http://127.0.0.1:8004'

export function toMediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  if (normalizedPath.startsWith('/uploads/')) return `${USER_MEDIA_BASE_URL}${normalizedPath}`
  return `${API_BASE_URL}${normalizedPath}`
}

export function uploadPath(filename, service = 'restaurant') {
  if (!filename) return ''
  if (filename.startsWith('http://') || filename.startsWith('https://')) return filename
  const cleanFilename = filename.replace(/^\/?uploads\/?/, '')
  const base = service === 'review' ? REVIEW_MEDIA_BASE_URL : RESTAURANT_MEDIA_BASE_URL
  return `${base}/uploads/${cleanFilename}`
}
