import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { unifiedApiClient, createCacheConfig, createLoadingConfig, DEFAULT_RETRY_CONFIG, type ApiConfig } from '@/api/unifiedApiClient'
import type { CacheConfig, LoadingConfig, RetryConfig } from '@/api/unifiedApiClient'
import { marketDataWebSocket, tradingWebSocket, riskWebSocket, WebSocketState } from '@/utils/webSocketManager'
import type { WebSocketMessage } from '@/utils/webSocketManager'

export interface StoreState<T = any> {
  data: T | null
  loading: boolean
  error: string | null
  lastFetch: number | null
}

export interface StoreActions<T = any> {
  fetch: (params?: any) => Promise<T>
  refresh: (params?: any) => Promise<T>
  clear: () => void
  setData: (data: T) => void
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}

export interface StoreConfig<T = any> {
  id: string
  endpoint: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  cache?: CacheConfig
  retry?: RetryConfig
  loading?: LoadingConfig
  transform?: (data: any) => T
  validate?: (data: any) => boolean
  initialData?: T
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
  static createApiStore<T = any>(config: StoreConfig<T>) {
    const {
      id,
      endpoint,
      method = 'GET',
      cache,
      retry = DEFAULT_RETRY_CONFIG,
      loading: loadingConfig,
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

      // Getters
      const isStale = computed(() => {
        if (!cache?.enabled || !lastFetch.value) return false
        return Date.now() - lastFetch.value > cache.ttl
      })

      const hasData = computed(() => data.value !== null)
      const isLoading = computed(() => loading.value)
      const hasError = computed(() => error.value !== null)

      // Actions
      const setData = (newData: T) => {
        if (validate && !validate(newData)) {
          throw new Error('Data validation failed')
        }

        data.value = transform ? transform(newData) : newData
        error.value = null
        lastFetch.value = Date.now()
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
      }

      const fetch = async (params?: any): Promise<T> => {
        try {
          setLoading(true)
          setError(null)

          const apiConfig: ApiConfig = {
            cache: cache ? {
              ...cache,
              enabled: cache.enabled ?? true,
              key: cache.key || `${id}-${JSON.stringify(params || {})}`
            } : undefined,
            retry,
            loading: loadingConfig
          }

          let result: any

          switch (method) {
            case 'GET':
              result = await unifiedApiClient.get(endpoint, apiConfig)
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

          setData(result)
          return data.value as T
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Fetch failed'
          setError(errorMessage)
          throw err
        } finally {
          setLoading(false)
        }
      }

      const refresh = async (params?: any): Promise<T> => {
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

        // Getters
        isStale,
        hasData,
        isLoading,
        hasError,

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
  static createPaginatedStore<T = any>(config: StoreConfig<T[]> & {
    pageSize?: number
    initialPage?: number
  }) {
    const { pageSize = 20, initialPage = 1, ...baseConfig } = config

    return defineStore(`${baseConfig.id}-paginated`, () => {
      // Base store
      const baseStore = PiniaStoreFactory.createApiStore<T[]>({
        ...baseConfig,
        transform: (data) => {
          // Assume API returns { items: T[], total: number, page: number }
          return baseConfig.transform ? baseConfig.transform(data.items || data) : (data.items || data)
        }
      })()

      // Pagination state
      const currentPage = ref(initialPage)
      const totalItems = ref(0)
      const totalPages = ref(0)

      // Getters
      const hasNextPage = computed(() => currentPage.value < totalPages.value)
      const hasPrevPage = computed(() => currentPage.value > 1)
      const isFirstPage = computed(() => currentPage.value === 1)
      const isLastPage = computed(() => currentPage.value === totalPages.value)

      // Actions
      const fetchPage = async (page: number = currentPage.value) => {
        const params = {
          page,
          page_size: pageSize,
        }

        const result = await baseStore.fetch(params)

        // Update pagination metadata (assuming API returns this info)
        // In practice, you'd extract this from the API response
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
        ...baseStore,

        // Pagination state
        currentPage,
        totalItems,
        totalPages,

        // Pagination getters
        hasNextPage,
        hasPrevPage,
        isFirstPage,
        isLastPage,

        // Pagination actions
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
  static createRealtimeStore<T = any>(config: StoreConfig<T> & {
    wsManager?: typeof marketDataWebSocket | typeof tradingWebSocket | typeof riskWebSocket
    wsChannel?: string
    updateInterval?: number
  }) {
    const { wsManager, wsChannel, updateInterval, ...baseConfig } = config

    return defineStore(`${baseConfig.id}-realtime`, () => {
      // Base store
      const baseStore = PiniaStoreFactory.createApiStore<T>(baseConfig)() as unknown as {
        setData: (data: any) => void
        refresh: () => Promise<any>
      }

      // Real-time state
      const isConnected = ref(false)
      const lastUpdate = ref<number | null>(null)
      const connectionState = ref<WebSocketState>(WebSocketState.DISCONNECTED)
      const pollingIntervalId = ref<number | null>(null)

      // Getters
      const isRealtime = computed(() => isConnected.value)
      const timeSinceLastUpdate = computed(() => {
        if (!lastUpdate.value) return null
        return Date.now() - lastUpdate.value
      })

      // Actions
      const connectWebSocket = async () => {
        if (!wsManager) return

        try {
          // Subscribe to connection state changes
          wsManager.onStateChange((state) => {
            connectionState.value = state
            isConnected.value = state === WebSocketState.CONNECTED
          })

          // Subscribe to data updates
          wsManager.on('update', (message: WebSocketMessage) => {
            if (message.channel === wsChannel && message.data) {
              baseStore.setData(message.data)
              lastUpdate.value = Date.now()
            }
          })

          // Connect to WebSocket
          await wsManager.connect()

          // Subscribe to channel if specified
          if (wsChannel) {
            wsManager.send({
              type: 'subscribe',
              channel: wsChannel
            })
          }
        } catch (error) {
          console.error(`Failed to connect WebSocket for ${baseConfig.id}:`, error)
          // Fall back to polling if WebSocket fails
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

        // Initial poll
        poll()

        // Set up interval
        pollingIntervalId.value = window.setInterval(poll, updateInterval)
      }

      const stopPolling = () => {
        if (pollingIntervalId.value) {
          clearInterval(pollingIntervalId.value)
          pollingIntervalId.value = null
        }
      }

      return {
        ...baseStore,

        // Real-time state
        isConnected,
        lastUpdate,
        connectionState,

        // Real-time getters
        isRealtime,
        timeSinceLastUpdate,

        // Real-time actions
        connectWebSocket,
        disconnectWebSocket,
        startPolling,
        stopPolling,
      }
    })
  }
}

// Convenience functions for common store types
export const createMarketDataStore = (id: string, endpoint: string) =>
  PiniaStoreFactory.createRealtimeStore({
    id,
    endpoint,
    method: 'GET',
    cache: createCacheConfig(`${id}-cache`, 'realtime'),
    loading: createLoadingConfig(`${id}-loading`),
    wsManager: marketDataWebSocket,
    wsChannel: 'market-data',
    updateInterval: 30000, // 30 seconds
  })

export const createReferenceDataStore = (id: string, endpoint: string) =>
  PiniaStoreFactory.createApiStore({
    id,
    endpoint,
    method: 'GET',
    cache: createCacheConfig(`${id}-cache`, 'reference'),
    loading: createLoadingConfig(`${id}-loading`),
  })

export const createUserDataStore = (id: string, endpoint: string) =>
  PiniaStoreFactory.createApiStore({
    id,
    endpoint,
    method: 'GET',
    cache: createCacheConfig(`${id}-cache`, 'user'),
    loading: createLoadingConfig(`${id}-loading`),
  })

export default PiniaStoreFactory