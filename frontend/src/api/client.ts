export const API_BASE_PATH = "/api"

export function apiFetch(path: string, init?: RequestInit) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`

  return fetch(`${API_BASE_PATH}${normalizedPath}`, init)
}
