export const ARTDECO_PAGE_ERROR_MESSAGE = '数据请求失败，请稍后重试'

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

export const toArtDecoPageMessage = (value: unknown): string =>
  typeof value === 'string' && value.trim().length > 0 ? value : ARTDECO_PAGE_ERROR_MESSAGE

export const extractArtDecoRequestIdFromHeaders = (headers: unknown): string => {
  if (!isRecord(headers)) return ''
  const traceHeader = headers['x-request-id']
  return typeof traceHeader === 'string' ? traceHeader : ''
}

export const normalizeArtDecoApiResult = (response: unknown): {
  payload: unknown
  requestId: string
  success: boolean
  message: string
} => {
  if (!isRecord(response)) {
    return { payload: response, requestId: '', success: true, message: '' }
  }

  const rootRequestId = typeof response.request_id === 'string'
    ? response.request_id
    : extractArtDecoRequestIdFromHeaders(response.headers)
  const rootSuccess = typeof response.success === 'boolean' ? response.success : true
  const rootMessage = typeof response.message === 'string' ? response.message : ''

  if (isRecord(response.data) && (typeof response.data.success === 'boolean' || typeof response.data.request_id === 'string')) {
    const nestedRequestId = typeof response.data.request_id === 'string'
      ? response.data.request_id
      : rootRequestId
    const nestedSuccess = typeof response.data.success === 'boolean'
      ? response.data.success
      : rootSuccess
    const nestedMessage = typeof response.data.message === 'string'
      ? response.data.message
      : rootMessage

    return {
      payload: 'data' in response.data ? response.data.data : response.data,
      requestId: nestedRequestId,
      success: nestedSuccess,
      message: nestedMessage
    }
  }

  return {
    payload: 'data' in response ? response.data : response,
    requestId: rootRequestId,
    success: rootSuccess,
    message: rootMessage
  }
}

export const isArtDecoPageDataEmpty = (
  pageData: unknown,
  shouldEvaluateEmptyState: boolean
): boolean => {
  if (!shouldEvaluateEmptyState) return false
  if (!pageData) return true
  if (Array.isArray(pageData) && pageData.length === 0) return true
  if (isRecord(pageData) && Object.keys(pageData).length === 0) return true
  return false
}

export const hasArtDecoPagePermission = (
  permission: string,
  authStoreValue: string | null
): boolean => {
  if (!permission) return true
  if (!authStoreValue) return true

  try {
    const auth = JSON.parse(authStoreValue)
    if (auth.permissions?.includes('*')) return true
    return auth.permissions?.includes(permission) || false
  } catch {
    return true
  }
}

export const shouldUseArtDecoRequestCache = (
  lastFetchTime: number,
  cacheTime: number,
  now = Date.now()
): boolean => {
  if (cacheTime === 0) return true
  return now - lastFetchTime > cacheTime
}
