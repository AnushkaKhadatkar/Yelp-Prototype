const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export function toMediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalizedPath}`
}

export function uploadPath(filename) {
  if (!filename) return ''
  return toMediaUrl(`/uploads/${filename}`)
}
