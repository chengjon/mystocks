import { defineStore, storeToRefs } from 'pinia'
import { ref, computed } from 'vue'
import { unifiedApiClient, createCacheConfig, createLoadingConfig, DEFAULT_RETRY_CONFIG } from '@/api/unifiedApiClient'
import { marketDataWebSocket, tradingWebSocket, riskWebSocket, WebSocketState } from '@/utils/webSocketManager'
import type { WebSocketMessage } from '@/utils/webSocketManager'

// Local type definitions for store configuration
interface CacheConfig {
  use?: boolean
  ttl?: number
  enabled?: boolean
  key?: string
  strategy?: 'memory' | 'sessionStorage' | 'localStorage'
}

interface LoadingConfig {
  show?: boolean
  enabled?: boolean
  key?: string
}

interface RetryConfig {
  retries?: number
  delay?: number
}

interface ApiConfig {
  endpoint: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  cache?: CacheConfig
  retry?: RetryConfig
  loading?: LoadingConfig
}

export interface StoreState<T = unknown> {
  data: T | null
  loading: boolean
  error: string | null
  lastFetch: number | null
  lastRequestId: string | null
  lastProcessTime: string | null
  requestCount: number
  errorCount: number
  lastDurationMs: number | null
  averageDurationMs: number | null
}

export interface StoreActions<T = unknown> {
  fetch: (params?: unknown) => Promise<T>
  refresh: (params?: unknown) => Promise<T>
  clear: () => void
  setData: (data: T) => void
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}

export interface StoreConfig<T = unknown> {
  id: string
  endpoint: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  cache?: CacheConfig
  retry?: RetryConfig
  loading?: LoadingConfig
  request?: (params?: unknown) => Promise<unknown>
  transform?: (data: unknown) => T
  validate?: (data: unknown) => boolean
  initialData?: T
}

type BaseStoreBinding<T> = ReturnType<ReturnType<typeof PiniaStoreFactory.createApiStore<T>>>

function bindBaseStore<T>(baseStore: BaseStoreBinding<T>) {
  return {
    ...storeToRefs(baseStore),
    fetch: baseStore.fetch,
    refresh: baseStore.refresh,
    clear: baseStore.clear,
    setData: baseStore.setData,
    setError: baseStore.setError,
    setLoading: baseStore.setLoading,
  }
}

function extractTraceMetadata(payload: unknown) {
  if (!payload || typeof payload !== 'object') {
    return { requestId: null, processTime: null }
  }

  const tracePayload = payload as { request_id?: unknown; process_time?: unknown }
  return {
    requestId: typeof tracePayload.request_id === 'string' && tracePayload.request_id.length > 0 ? tracePayload.request_id : null,
    processTime: typeof tracePayload.process_time === 'string' && tracePayload.process_time.length > 0 ? tracePayload.process_time : null,
  }
}

/**
 * Pinia Store Factory for API Data Management
 *
 * Creates standardized Pinia stores with consistent patterns for:
 * - Data fetching and caching
 * - Loading states
 * - Error handling
 * - Data transformation
 * - Validation
 */
export class PiniaStoreFactory {
  /**
   * Create a basic API data store
   */
  static createApiStore<T = unknown>(config: StoreConfig<T>) {
    const {
      id,
      endpoint,
      method = 'GET',
      cache,
      retry = DEFAULT_RETRY_CONFIG,
      loading: loadingConfig,
      request,
      transform,
      validate,
      initialData = null
    } = config

    return defineStore(id, () => {
      // State
      const data = ref<T | null>(initialData)
      const loading = ref(false)
      const error = ref<string | null>(null)
      const lastFetch = ref<number | null>(null)
      const lastRequestId = ref<string | null>(null)
      const lastProcessTime = ref<string | null>(null)
      const requestCount = ref(0)
      const errorCount = ref(0)
      const totalDurationMs = ref(0)
      const lastDurationMs = ref<number | null>(null)

      // Getters
      const isStale = computed(() => {
        if (!cache?.enabled || !lastFetch.value) return false
        return Date.now() - lastFetch.value > (cache.ttl || 0)
      })

      const hasData = computed(() => data.value !== null)
      const isLoading = computed(() => loading.value)
      const hasError = computed(() => error.value !== null)
      const averageDurationMs = computed(() => {
        if (requestCount.value === 0) {
          return null
        }
        return Math.round(totalDurationMs.value / requestCount.value)
      })

      // Actions
      const setData = (newData: T) => {
        if (validate && !validate(newData)) {
          throw new Error('Data validation failed')
        }

        data.value = transform ? transform(newData) : newData
        error.value = null
        lastFetch.value = Date.now()
        const trace = extractTraceMetadata(newData)
        lastRequestId.value = trace.requestId
        lastProcessTime.value = trace.processTime
      }

      const setError = (newError: string | null) => {
        error.value = newError
        if (newError) {
          loading.value = false
        }
      }

      const setLoading = (newLoading: boolean) => {
        loading.value = newLoading
      }

      const clear = () => {
        data.value = initialData
        error.value = null
        loading.value = false
        lastFetch.value = null
        lastRequestId.value = null
        lastProcessTime.value = null
      }

      const fetch = async (params?: unknown): Promise<T> => {
        const startTime = Date.now()
        try {
          setLoading(true)
          setError(null)

          const apiConfig: Partial<ApiConfig> = {
            cache: cache ? {
              ...cache,
              enabled: cache.enabled ?? true,
              key: cache.key || `${id}-${JSON.stringify(params || {})}`
            } : undefined,
            retry,
            loading: loadingConfig
          }

          let result: unknown

          if (request) {
            result = await request(params)
          } else {
          switch (method) {
              case 'GET':
                result = await unifiedApiClient.get(endpoint, {
                  ...apiConfig,
                  params: params as Record<string, unknown> | undefined
                })
                break
              case 'POST':
                result = await unifiedApiClient.post(endpoint, params, apiConfig)
                break
              case 'PUT':
                result = await unifiedApiClient.put(endpoint, params, apiConfig)
                break
              case 'DELETE':
                result = await unifiedApiClient.delete(endpoint, apiConfig)
                break
              default:
                throw new Error(`Unsupported method: ${method}`)
            }
          }

          setData(result as T)
          requestCount.value += 1
          lastDurationMs.value = Date.now() - startTime
          totalDurationMs.value += lastDurationMs.value
          return data.value as T
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Fetch failed'
          setError(errorMessage)
          requestCount.value += 1
          errorCount.value += 1
          lastDurationMs.value = Date.now() - startTime
          totalDurationMs.value += lastDurationMs.value
          throw err
        } finally {
          setLoading(false)
        }
      }

      const refresh = async (params?: unknown): Promise<T> => {
        // Force refresh by clearing cache if enabled
        if (cache?.enabled) {
          // Note: In a real implementation, you'd need to clear the specific cache entry
          // For now, we'll just fetch again
        }
        return fetch(params)
      }

      return {
        // State
        data,
        loading,
        error,
        lastFetch,
        lastRequestId,
        lastProcessTime,
        requestCount,
        errorCount,
        lastDurationMs,

        // Getters
        isStale,
        hasData,
        isLoading,
        hasError,
        averageDurationMs,

        // Actions
        fetch,
        refresh,
        clear,
        setData,
        setError,
        setLoading,
      }
    })
  }

  /**
   * Create a paginated data store
   */
  static createPaginatedStore<T = unknown>(config: StoreConfig<T[]> & {
    pageSize?: number
    initialPage?: number
  }) {
    const { pageSize = 20, initialPage = 1, ...baseConfig } = config

    return defineStore(`${baseConfig.id}-paginated`, () => {
      // Base store
      const baseStore = PiniaStoreFactory.createApiStore<T[]>({
        ...baseConfig,
        transform: (data: unknown) => {
          const dataObj = data as { items?: T[]; [key: string]: unknown }
          return baseConfig.transform ? baseConfig.transform(dataObj.items || data) : (dataObj.items || data) as T[]
        }
      })()

      const currentPage = ref(initialPage)
      const totalItems = ref(0)
      const totalPages = ref(0)
      const hasNextPage = computed(() => currentPage.value < totalPages.value)
      const hasPrevPage = computed(() => currentPage.value > 1)
      const isFirstPage = computed(() => currentPage.value === 1)
      const isLastPage = computed(() => currentPage.value === totalPages.value)
      const fetchPage = async (page: number = currentPage.value) => {
        const result = await baseStore.fetch({ page, page_size: pageSize })
        currentPage.value = page
        return result
      }

      const nextPage = async () => {
        if (hasNextPage.value) {
          return fetchPage(currentPage.value + 1)
        }
      }

      const prevPage = async () => {
        if (hasPrevPage.value) {
          return fetchPage(currentPage.value - 1)
        }
      }

      const goToPage = async (page: number) => {
        if (page >= 1 && page <= totalPages.value) {
          return fetchPage(page)
        }
      }

      return {
        ...bindBaseStore(baseStore),
        currentPage,
        totalItems,
        totalPages,
        hasNextPage,
        hasPrevPage,
        isFirstPage,
        isLastPage,
        fetchPage,
        nextPage,
        prevPage,
        goToPage,
      }
    })
  }

  /**
   * Create a real-time data store with WebSocket support
   */
  static createRealtimeStore<T = unknown>(config: StoreConfig<T> & {
    wsManager?: typeof marketDataWebSocket | typeof tradingWebSocket | typeof riskWebSocket
    wsChannel?: string
    updateInterval?: number
  }) {
    const { wsManager, wsChannel, updateInterval, ...baseConfig } = config

    return defineStore(`${baseConfig.id}-realtime`, () => {
      const baseStore = PiniaStoreFactory.createApiStore<T>(baseConfig)() as unknown as {
        fetch: (params?: unknown) => Promise<unknown>
        setData: (data: unknown) => void
        setError: (error: string | null) => void
        setLoading: (loading: boolean) => void
        refresh: () => Promise<unknown>
        clear: () => void
      }
      const isConnected = ref(false)
      const lastUpdate = ref<number | null>(null)
      const connectionState = ref<WebSocketState>(WebSocketState.DISCONNECTED)
      const pollingIntervalId = ref<number | null>(null)
      const isRealtime = computed(() => isConnected.value)
      const timeSinceLastUpdate = computed(() => {
        if (!lastUpdate.value) return null
        return Date.now() - lastUpdate.value
      })
      const connectWebSocket = async () => {
        if (!wsManager) return

        try {
          wsManager.onStateChange((state) => {
            connectionState.value = state
            isConnected.value = state === WebSocketState.CONNECTED
          })

          wsManager.on('update', (message: WebSocketMessage) => {
            if (message.channel === wsChannel && message.data) {
              baseStore.setData(message.data)
              lastUpdate.value = Date.now()
            }
          })

          await wsManager.connect()

          if (wsChannel) {
            wsManager.send({
              type: 'subscribe',
              channel: wsChannel
            })
          }
        } catch (error) {
          console.error(`Failed to connect WebSocket for ${baseConfig.id}:`, error)
          startPolling()
        }
      }

      const disconnectWebSocket = () => {
        if (wsManager) {
          wsManager.disconnect()
        }
        stopPolling()
        isConnected.value = false
        connectionState.value = WebSocketState.DISCONNECTED
      }

      const startPolling = () => {
        if (!updateInterval || pollingIntervalId.value) return

        const poll = async () => {
          try {
            await baseStore.refresh()
            lastUpdate.value = Date.now()
          } catch (error) {
            console.error('Polling failed:', error)
          }
        }

        poll()
        pollingIntervalId.value = window.setInterval(poll, updateInterval)
      }

      const stopPolling = () => {
        if (pollingIntervalId.value) {
          clearInterval(pollingIntervalId.value)
          pollingIntervalId.value = null
        }
      }

      return {
        ...bindBaseStore(baseStore as BaseStoreBinding<T>),
        isConnected,
        lastUpdate,
        connectionState,
        isRealtime,
        timeSinceLastUpdate,
        connectWebSocket,
        disconnectWebSocket,
        startPolling,
        stopPolling,
      }
    })
  }
}

export const createMarketDataStore = (id: string, endpoint: string) =>
  PiniaStoreFactory.createRealtimeStore({
    id,
    endpoint,
    method: 'GET',
    cache: createCacheConfig(true),
    loading: createLoadingConfig(true),
    wsManager: marketDataWebSocket,
    wsChannel: 'market-data',
    updateInterval: 30000,
  })

export const createReferenceDataStore = (id: string, endpoint: string) =>
  PiniaStoreFactory.createApiStore({
    id,
    endpoint,
    method: 'GET',
    cache: createCacheConfig(true),
    loading: createLoadingConfig(true),
  })

export const createUserDataStore = (id: string, endpoint: string) =>
  PiniaStoreFactory.createApiStore({
    id,
    endpoint,
    method: 'GET',
    cache: createCacheConfig(true),
    loading: createLoadingConfig(true),
  })

export default PiniaStoreFactory
