import { computed, ref } from 'vue'

export type BackendReadinessState = 'checking' | 'ready' | 'error'

interface ReadinessPayload {
  status?: string
}

interface UnifiedReadinessResponse {
  success?: boolean
  message?: string
  request_id?: string
  data?: ReadinessPayload | null
}

interface BackendReadinessResult {
  ready: boolean
  backendReady: boolean
  usingMockFallback: boolean
  message: string
  requestId: string
}

const READINESS_TIMEOUT_MS = 30000

export function resolveReadinessEndpoint(apiBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '/api')): string {
  const normalizedBase = apiBaseUrl.trim().replace(/\/+$/, '') || '/api'

  if (normalizedBase === '/api' || normalizedBase.endsWith('/api')) {
    return `${normalizedBase}/health/ready`
  }

  return `${normalizedBase}/api/health/ready`
}

export async function requestBackendReadiness(
  fetchImpl: typeof fetch = fetch,
  apiBaseUrl?: string,
  mockModeEnabled = Boolean(import.meta.env.VITE_USE_MOCK_DATA)
): Promise<BackendReadinessResult> {
  const endpoint = resolveReadinessEndpoint(apiBaseUrl)
  const controller = new AbortController()
  const timeoutId = globalThis.setTimeout(() => controller.abort(), READINESS_TIMEOUT_MS)

  try {
    const response = await fetchImpl(endpoint, {
      method: 'GET',
      cache: 'no-store',
      headers: {
        Accept: 'application/json'
      },
      signal: controller.signal
    })

    const payload = (await response.json().catch(() => null)) as UnifiedReadinessResponse | null
    const requestId = payload?.request_id || ''
    const ready = response.ok && payload?.success !== false && payload?.data?.status === 'ready'

    if (ready) {
      return {
        ready: true,
        backendReady: true,
        usingMockFallback: false,
        message: payload?.message || '后端已就绪',
        requestId
      }
    }

    const failureMessage = payload?.message || `Readiness probe failed with status ${response.status}`
    if (mockModeEnabled) {
      return {
        ready: true,
        backendReady: false,
        usingMockFallback: true,
        message: `后端暂未就绪，已切换 Mock 验收模式：${failureMessage}`,
        requestId
      }
    }

    return {
      ready: false,
      backendReady: false,
      usingMockFallback: false,
      message: `后端暂未就绪：${failureMessage}`,
      requestId
    }
  } catch (error) {
    const failureMessage = error instanceof Error ? error.message : 'readiness probe request failed'

    if (mockModeEnabled) {
      return {
        ready: true,
        backendReady: false,
        usingMockFallback: true,
        message: `后端暂未就绪，已切换 Mock 验收模式：${failureMessage}`,
        requestId: ''
      }
    }

    return {
      ready: false,
      backendReady: false,
      usingMockFallback: false,
      message: `后端暂未就绪：${failureMessage}`,
      requestId: ''
    }
  } finally {
    globalThis.clearTimeout(timeoutId)
  }
}

export function useBackendReadiness() {
  const readinessState = ref<BackendReadinessState>('checking')
  const readinessMessage = ref('正在检查后端就绪状态...')
  const requestId = ref('')
  const backendReady = ref(false)
  const usingMockFallback = ref(false)

  const isChecking = computed(() => readinessState.value === 'checking')
  const hasBlockingReadinessError = computed(() => readinessState.value === 'error')

  async function checkBackendReadiness() {
    readinessState.value = 'checking'
    readinessMessage.value = '正在检查后端就绪状态...'

    const result = await requestBackendReadiness()

    backendReady.value = result.backendReady
    usingMockFallback.value = result.usingMockFallback
    requestId.value = result.requestId
    readinessMessage.value = result.message
    readinessState.value = result.ready ? 'ready' : 'error'

    return result
  }

  return {
    readinessState,
    readinessMessage,
    requestId,
    backendReady,
    usingMockFallback,
    isChecking,
    hasBlockingReadinessError,
    checkBackendReadiness
  }
}
