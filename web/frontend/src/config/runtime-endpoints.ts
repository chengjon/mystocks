const isDev = import.meta.env.DEV

const trimValue = (value: unknown): string => {
  if (typeof value !== 'string') {
    return ''
  }
  return value.trim()
}

const toWsProtocol = (protocol: string): string => (protocol === 'https:' ? 'wss:' : 'ws:')

const apiBaseFromEnv = trimValue(import.meta.env.VITE_API_BASE_URL)
const wsBaseFromEnv = trimValue(import.meta.env.VITE_WS_BASE_URL)

const browserApiBase =
  typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.host}` : ''

const defaultApiBase = isDev ? '/api' : browserApiBase

export const API_BASE_URL = apiBaseFromEnv || defaultApiBase

const derivedWsBase = (() => {
  const source = API_BASE_URL
  if (source.startsWith('https://')) {
    return `wss://${source.slice('https://'.length)}`
  }
  if (source.startsWith('http://')) {
    return `ws://${source.slice('http://'.length)}`
  }
  if (source.startsWith('/') && typeof window !== 'undefined') {
    return `${toWsProtocol(window.location.protocol)}//${window.location.host}`
  }
  if (typeof window !== 'undefined') {
    return `${toWsProtocol(window.location.protocol)}//${window.location.host}`
  }
  return ''
})()

export const WS_BASE_URL = wsBaseFromEnv || derivedWsBase

export const apiUrl = (path: string): string => {
  if (!path) return API_BASE_URL
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}

export const wsUrl = (path: string): string => {
  if (!path) return WS_BASE_URL
  return `${WS_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}
