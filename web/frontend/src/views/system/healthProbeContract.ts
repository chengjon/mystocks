import type { UnifiedResponse } from '@/api/types/common'

function isUnifiedResponse<T>(payload: unknown): payload is UnifiedResponse<T> {
  return Boolean(
    payload &&
      typeof payload === 'object' &&
      'success' in payload &&
      typeof (payload as { success?: unknown }).success === 'boolean'
  )
}

export function normalizeSystemHealthProbeResponse<T>(payload: unknown): UnifiedResponse<T> {
  if (isUnifiedResponse<T>(payload)) {
    return payload
  }

  const record = payload && typeof payload === 'object' ? payload as Record<string, unknown> : {}
  const timestamp = typeof record.timestamp === 'string' ? record.timestamp : new Date().toISOString()
  const requestId = typeof record.request_id === 'string' ? record.request_id : ''
  const processTime = typeof record.process_time === 'string' ? record.process_time : undefined

  return {
    success: true,
    code: 200,
    message: 'health probe ok',
    data: payload as T,
    timestamp,
    request_id: requestId,
    process_time: processTime,
    errors: null,
  }
}
