import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useMarketQuotesStore, useTradingHistoryStore } from '@/stores/apiStores'
import { unifiedApiClient } from '@/api/unifiedApiClient'

vi.mock('@/api/unifiedApiClient', () => ({
  unifiedApiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  createCacheConfig: vi.fn((enabled) => ({ enabled, ttl: 300000, strategy: 'memory' })),
  createLoadingConfig: vi.fn((enabled) => ({ enabled })),
  DEFAULT_RETRY_CONFIG: { retries: 0 }
}))

const { websocketStub } = vi.hoisted(() => ({
  websocketStub: {
    onStateChange: vi.fn(),
    on: vi.fn(),
    connect: vi.fn().mockResolvedValue(undefined),
    disconnect: vi.fn(),
    send: vi.fn(),
  }
}))

vi.mock('@/utils/webSocketManager', () => ({
  marketDataWebSocket: websocketStub,
  tradingWebSocket: websocketStub,
  riskWebSocket: websocketStub,
  WebSocketState: {
    DISCONNECTED: 'DISCONNECTED',
    CONNECTED: 'CONNECTED'
  }
}))

describe('factory-created api stores', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('provides a realtime market quotes store', async () => {
    const store = useMarketQuotesStore()

    expect(store).toHaveProperty('connectWebSocket')
    expect(store).toHaveProperty('disconnectWebSocket')
    expect(store).toHaveProperty('isRealtime')
    expect(store.isConnected).toBe(false)

    await store.connectWebSocket()

    expect(websocketStub.connect).toHaveBeenCalledTimes(1)
    expect(websocketStub.send).toHaveBeenCalledWith({
      type: 'subscribe',
      channel: 'market-data'
    })
  })

  it('provides a paginated trading history store with cache-aware fetch config', async () => {
    unifiedApiClient.get.mockResolvedValue([{ id: 1, symbol: '000001' }])

    const store = useTradingHistoryStore()
    await store.fetchPage(2)

    expect(store.currentPage).toBe(2)
    expect(unifiedApiClient.get).toHaveBeenCalledWith(
      '/api/trading/history',
      expect.objectContaining({
        cache: expect.objectContaining({
          enabled: true,
          key: 'trading-history'
        }),
        params: {
          page: 2,
          page_size: 20
        }
      })
    )
  })
})
