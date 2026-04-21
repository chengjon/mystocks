import { computed, nextTick, onMounted, ref, watch, type ComponentPublicInstance, type Slots } from 'vue'
import { useApiService } from '@/composables/useApiService'

type ApiMethod = 'GET' | 'POST'

export interface ArtDecoPageConfig {
  title: string
  subtitle?: string
  showStatus?: boolean
  statusText?: string
  statusType?: 'success' | 'warning' | 'error' | 'info'
  showRefresh?: boolean
  showStats?: boolean
  showTabs?: boolean
  showTraceId?: boolean
  apiUrl?: string
  apiMethod?: ApiMethod
  apiParams?: Record<string, unknown>
  skeleton?: {
    columns?: number
    rows?: number
  }
  emptyMessage?: string
  permission: string
  cacheTime?: number
}

export interface StatItem {
  label: string
  value: string | number
  change?: number
  changePercent?: boolean
  variant?: 'default' | 'gold' | 'rise' | 'fall'
  size?: 'small' | 'medium' | 'large'
}

export interface TabItem {
  key: string
  label: string
  icon?: string
}

interface ArtDecoPageTemplateProps {
  pageConfig: ArtDecoPageConfig
  stats: StatItem[]
  tabs: TabItem[]
  defaultTab: string
}

type ArtDecoPageTemplateEmit = {
  (event: 'tab-change', tabKey: string): void
  (event: 'data-loaded', data: unknown): void
  (event: 'data-error', error: Error): void
}

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

export function useArtDecoPageTemplate(
  props: Readonly<ArtDecoPageTemplateProps>,
  slots: Slots,
  emit: ArtDecoPageTemplateEmit
) {
  const { loading, error, getData, postData } = useApiService()

  const hasError = ref(false)
  const dataLoaded = ref(false)
  const pageData = ref<unknown>(null)
  const lastRequestId = ref('')
  const lastFetchTime = ref(0)
  const tabButtonRefs = ref<Array<HTMLButtonElement | null>>([])

  const resolveDefaultTab = (): string => {
    if (props.defaultTab && props.tabs.some((tab) => tab.key === props.defaultTab)) {
      return props.defaultTab
    }
    return props.tabs[0]?.key || ''
  }

  const activeTab = ref(resolveDefaultTab())

  const statusText = computed(() => props.pageConfig.statusText || (loading.value ? '加载中...' : '正常'))
  const statusType = computed(() => props.pageConfig.statusType || (hasError.value ? 'error' : 'success'))
  const errorMessage = computed(() => {
    const currentError = error.value as unknown
    if (isRecord(currentError) && typeof currentError.message === 'string') {
      return currentError.message
    }
    return '数据请求失败，请稍后重试'
  })

  const showStatsSection = computed(() =>
    Boolean(slots.stats) || (props.pageConfig.showStats === true && props.stats.length > 0)
  )

  const showTabsSection = computed(() =>
    Boolean(slots.tabs) || (props.pageConfig.showTabs === true && props.tabs.length > 0)
  )

  const shouldEvaluateEmptyState = computed(() => Boolean(props.pageConfig.apiUrl))

  const isEmptyData = computed(() => isArtDecoPageDataEmpty(pageData.value, shouldEvaluateEmptyState.value))

  const hasPermission = (permission: string): boolean => {
    return hasArtDecoPagePermission(permission, localStorage.getItem('auth-store'))
  }

  const shouldFetchData = (): boolean => {
    const cacheTime = props.pageConfig.cacheTime || 0
    return shouldUseArtDecoRequestCache(lastFetchTime.value, cacheTime)
  }

  const tabButtonId = (tabKey: string): string => `artdeco-tab-${tabKey || 'default'}`
  const tabPanelId = (tabKey: string): string => `artdeco-panel-${tabKey || 'default'}`

  const setTabButtonRef = (el: Element | ComponentPublicInstance | null, index: number) => {
    if (el instanceof HTMLButtonElement) {
      tabButtonRefs.value[index] = el
      return
    }
    if (el && '$el' in el && (el as ComponentPublicInstance).$el instanceof HTMLButtonElement) {
      tabButtonRefs.value[index] = (el as ComponentPublicInstance).$el as HTMLButtonElement
      return
    }
    tabButtonRefs.value[index] = null
  }

  const handleTabChange = (tabKey: string) => {
    if (!tabKey || activeTab.value === tabKey) return
    activeTab.value = tabKey
    emit('tab-change', tabKey)
  }

  const handleTabKeydown = async (event: KeyboardEvent, index: number) => {
    if (props.tabs.length === 0) return

    let nextIndex = index
    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        nextIndex = (index + 1) % props.tabs.length
        break
      case 'ArrowLeft':
      case 'ArrowUp':
        nextIndex = (index - 1 + props.tabs.length) % props.tabs.length
        break
      case 'Home':
        nextIndex = 0
        break
      case 'End':
        nextIndex = props.tabs.length - 1
        break
      default:
        return
    }

    event.preventDefault()
    const nextTab = props.tabs[nextIndex]
    if (!nextTab) return

    handleTabChange(nextTab.key)
    await nextTick()
    tabButtonRefs.value[nextIndex]?.focus()
  }

  const handleRefresh = async () => {
    if (!props.pageConfig.apiUrl) {
      dataLoaded.value = true
      return
    }

    hasError.value = false
    error.value = null

    try {
      const method = props.pageConfig.apiMethod || 'GET'
      const params = props.pageConfig.apiParams || {}
      const response = method === 'POST'
        ? await postData(props.pageConfig.apiUrl, params)
        : await getData(props.pageConfig.apiUrl, params)

      const normalized = normalizeArtDecoApiResult(response)
      if (!normalized.success) {
        throw new Error(toArtDecoPageMessage(normalized.message))
      }

      pageData.value = normalized.payload
      lastRequestId.value = normalized.requestId
      lastFetchTime.value = Date.now()
      dataLoaded.value = true
      emit('data-loaded', pageData.value)
    } catch (err: unknown) {
      hasError.value = true
      const normalizedError = err instanceof Error ? err : new Error(ARTDECO_PAGE_ERROR_MESSAGE)
      console.error(`[ArtDecoPage] ${props.pageConfig.title} 数据请求失败:`, normalizedError)
      emit('data-error', normalizedError)
    }
  }

  watch(
    () => [props.pageConfig.apiUrl, props.pageConfig.apiMethod, props.pageConfig.apiParams] as const,
    () => {
      if (!props.pageConfig.apiUrl) {
        dataLoaded.value = true
        hasError.value = false
        return
      }
      if (shouldFetchData()) {
        handleRefresh()
      }
    },
    { deep: true }
  )

  watch(
    () => [props.tabs, props.defaultTab] as const,
    () => {
      const resolvedTab = resolveDefaultTab()
      if (!props.tabs.some((tab) => tab.key === activeTab.value)) {
        activeTab.value = resolvedTab
      }
    },
    { deep: true }
  )

  onMounted(() => {
    activeTab.value = resolveDefaultTab()
    if (props.pageConfig.apiUrl && shouldFetchData()) {
      handleRefresh()
    } else {
      dataLoaded.value = true
    }
  })

  return {
    loading,
    error,
    hasError,
    dataLoaded,
    pageData,
    lastRequestId,
    activeTab,
    statusText,
    statusType,
    errorMessage,
    showStatsSection,
    showTabsSection,
    isEmptyData,
    hasPermission,
    tabButtonId,
    tabPanelId,
    setTabButtonRef,
    handleTabChange,
    handleTabKeydown,
    handleRefresh
  }
}
