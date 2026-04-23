const isDev = import.meta.env.DEV
const LOOPBACK_HOSTS = new Set(['localhost', '127.0.0.1'])

type BrowserLocationLike = Pick<Location, 'protocol' | 'host' | 'hostname' | 'origin'>

const trimValue = (value: unknown): string => {
  if (typeof value !== 'string') {
    return ''
  }
  return value.trim()
}

const toWsProtocol = (protocol: string): string => (protocol === 'https:' ? 'wss:' : 'ws:')

const apiBaseFromEnv = trimValue(import.meta.env.VITE_API_BASE_URL)
const wsBaseFromEnv = trimValue(import.meta.env.VITE_WS_BASE_URL)

function getBrowserApiBase(locationLike?: BrowserLocationLike): string {
  return locationLike ? `${locationLike.protocol}//${locationLike.host}` : ''
}

export function resolveRuntimeApiBase(
  apiBaseUrl = apiBaseFromEnv,
  locationLike: BrowserLocationLike | undefined = typeof window !== 'undefined' ? window.location : undefined,
  devMode = isDev
): string {
  const normalizedEnvBase = trimValue(apiBaseUrl)
  const browserApiBase = getBrowserApiBase(locationLike)
  const defaultApiBase = devMode ? '/api' : browserApiBase

  if (!normalizedEnvBase) {
    return defaultApiBase
  }

  if (!devMode || !locationLike) {
    return normalizedEnvBase
  }

  try {
    const parsedBase = new URL(normalizedEnvBase)
    if (
      (parsedBase.protocol === 'http:' || parsedBase.protocol === 'https:') &&
      LOOPBACK_HOSTS.has(parsedBase.hostname) &&
      LOOPBACK_HOSTS.has(locationLike.hostname) &&
      parsedBase.origin !== locationLike.origin
    ) {
      return '/api'
    }
  } catch {
    return normalizedEnvBase
  }

  return normalizedEnvBase
}

export const API_BASE_URL = resolveRuntimeApiBase()

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
