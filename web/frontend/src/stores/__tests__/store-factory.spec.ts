import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { PiniaStoreFactory } from '@/stores/storeFactory'
import { unifiedApiClient } from '@/api/unifiedApiClient'

// Mock the unified API client
vi.mock('@/api/unifiedApiClient', () => ({
  unifiedApiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  createCacheConfig: vi.fn((key, strategy) => ({ enabled: true, key, ttl: 300000, strategy })),
  createLoadingConfig: vi.fn((key) => ({ enabled: true, key })),
  DEFAULT_RETRY_CONFIG: { enabled: true, maxAttempts: 3, delay: 1000, backoffFactor: 2 }
}))

describe('PiniaStoreFactory', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('createApiStore', () => {
    it('should create a basic API store with correct structure', () => {
      const store = PiniaStoreFactory.createApiStore({
        id: 'test-store',
        endpoint: '/api/test',
        method: 'GET'
      })

      const storeInstance = store()

      expect(storeInstance).toHaveProperty('data')
      expect(storeInstance).toHaveProperty('loading')
      expect(storeInstance).toHaveProperty('error')
      expect(storeInstance).toHaveProperty('lastFetch')
      expect(storeInstance).toHaveProperty('fetch')
      expect(storeInstance).toHaveProperty('refresh')
      expect(storeInstance).toHaveProperty('clear')
      expect(storeInstance).toHaveProperty('setData')
      expect(storeInstance).toHaveProperty('setError')
      expect(storeInstance).toHaveProperty('setLoading')
    })

    it('should handle successful API calls', async () => {
      const mockData = { id: 1, name: 'Test' }
      unifiedApiClient.get.mockResolvedValue(mockData)

      const store = PiniaStoreFactory.createApiStore({
        id: 'test-store',
        endpoint: '/api/test'
      })

      const storeInstance = store()
      const result = await storeInstance.fetch()

      expect(unifiedApiClient.get).toHaveBeenCalledWith('/api/test', expect.any(Object))
      expect(result).toEqual(mockData)
      expect(storeInstance.data).toEqual(mockData)
      expect(storeInstance.loading).toBe(false)
      expect(storeInstance.error).toBeNull()
    })

    it('should handle API errors', async () => {
      const errorMessage = 'API Error'
      unifiedApiClient.get.mockRejectedValue(new Error(errorMessage))

      const store = PiniaStoreFactory.createApiStore({
        id: 'test-store',
        endpoint: '/api/test'
      })

      const storeInstance = store()

      await expect(storeInstance.fetch()).rejects.toThrow(errorMessage)
      expect(storeInstance.loading).toBe(false)
      expect(storeInstance.error).toBe(errorMessage)
    })

    it('should use custom transform function', async () => {
      const apiResponse = { items: [{ id: 1 }, { id: 2 }] }
      const transformedData = [{ id: 1 }, { id: 2 }]

      unifiedApiClient.get.mockResolvedValue(apiResponse)

      const store = PiniaStoreFactory.createApiStore({
        id: 'test-store',
        endpoint: '/api/test',
        transform: (data) => data.items
      })

      const storeInstance = store()
      await storeInstance.fetch()

      expect(storeInstance.data).toEqual(transformedData)
    })

    it('should validate data with custom validator', async () => {
      const validData = { id: 1, requiredField: 'present' }
      unifiedApiClient.get.mockResolvedValue(validData)

      const store = PiniaStoreFactory.createApiStore({
        id: 'test-store',
        endpoint: '/api/test',
        validate: (data) => data.id && data.requiredField
      })

      const storeInstance = store()
      await storeInstance.fetch()

      expect(storeInstance.data).toEqual(validData)
    })

    it('should reject invalid data', async () => {
      const invalidData = { id: 1 } // missing requiredField
      unifiedApiClient.get.mockResolvedValue(invalidData)

      const store = PiniaStoreFactory.createApiStore({
        id: 'test-store',
        endpoint: '/api/test',
        validate: (data) => data.id && data.requiredField
      })

      const storeInstance = store()

      await expect(storeInstance.fetch()).rejects.toThrow('Data validation failed')
    })
  })

  describe('createPaginatedStore', () => {
    it('should create a paginated store with pagination controls', () => {
      const store = PiniaStoreFactory.createPaginatedStore({
        id: 'paginated-store',
        endpoint: '/api/items'
      })

      const storeInstance = store()

      expect(storeInstance).toHaveProperty('currentPage')
      expect(storeInstance).toHaveProperty('totalItems')
      expect(storeInstance).toHaveProperty('totalPages')
      expect(storeInstance).toHaveProperty('hasNextPage')
      expect(storeInstance).toHaveProperty('hasPrevPage')
      expect(storeInstance).toHaveProperty('fetchPage')
      expect(storeInstance).toHaveProperty('nextPage')
      expect(storeInstance).toHaveProperty('prevPage')
      expect(storeInstance).toHaveProperty('goToPage')
    })
  })

  describe('createRealtimeStore', () => {
    it('should create a real-time store with WebSocket capabilities', () => {
      const store = PiniaStoreFactory.createRealtimeStore({
        id: 'realtime-store',
        endpoint: '/api/realtime'
      })

      const storeInstance = store()

      expect(storeInstance).toHaveProperty('isConnected')
      expect(storeInstance).toHaveProperty('lastUpdate')
      expect(storeInstance).toHaveProperty('connectionState')
      expect(storeInstance).toHaveProperty('isRealtime')
      expect(storeInstance).toHaveProperty('timeSinceLastUpdate')
      expect(storeInstance).toHaveProperty('connectWebSocket')
      expect(storeInstance).toHaveProperty('disconnectWebSocket')
      expect(storeInstance).toHaveProperty('startPolling')
      expect(storeInstance).toHaveProperty('stopPolling')
    })
  })
})