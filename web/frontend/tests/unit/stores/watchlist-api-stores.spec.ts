import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { apiClient } from '@/api/apiClient'
import {
  createMonitoringWatchlistActions,
  useWatchlistsStore,
  useWatchlistStocksStore,
} from '@/stores/apiStores'

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('@/api/unifiedApiClient', () => ({
  unifiedApiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  createCacheConfig: vi.fn(),
  createLoadingConfig: vi.fn(),
  DEFAULT_RETRY_CONFIG: { retries: 3, delay: 1000 },
}))

vi.mock('@/utils/webSocketManager', () => ({
  tradingWebSocket: {},
  riskWebSocket: {},
  marketDataWebSocket: {},
  WebSocketState: { DISCONNECTED: 'DISCONNECTED' },
}))

describe('watchlist api stores', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('loads monitoring watchlists through the standardized watchlists store', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      success: true,
      request_id: 'req-monitoring-watchlists-1',
      data: [
        { id: 101, name: '核心止损监控', stocks_count: 2 },
      ],
    })

    const store = useWatchlistsStore()
    const result = await store.fetch()

    expect(apiClient.get).toHaveBeenCalledWith('/v1/monitoring/watchlists')
    expect(result).toEqual([
      {
        id: '101',
        name: '核心止损监控',
        stocks: [{}, {}],
      },
    ])
    expect(store.lastRequestId).toBe('req-monitoring-watchlists-1')
  })

  it('loads monitoring watchlist stocks by watchlist id through the standardized stocks store', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      success: true,
      request_id: 'req-monitoring-watchlist-stocks-1',
      data: [
        {
          stock_code: '600519',
          stock_name: '贵州茅台',
          entry_price: 1820,
          weight: 0.2,
        },
      ],
    })

    const store = useWatchlistStocksStore()
    const result = await store.fetch({ watchlistId: '101' })

    expect(apiClient.get).toHaveBeenCalledWith('/v1/monitoring/watchlists/101/stocks')
    expect(result).toEqual([
      {
        symbol: '600519',
        name: '贵州茅台',
        price: 1820,
        change: '--',
        volume: '--',
        weight: '20.00%',
        stock_code: '600519',
        stock_name: '贵州茅台',
        entry_price: 1820,
        stop_loss_price: undefined,
      },
    ])
    expect(store.lastRequestId).toBe('req-monitoring-watchlist-stocks-1')
  })

  it('creates and removes monitoring watchlist entries through standardized action helpers', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ success: true })
    vi.mocked(apiClient.delete).mockResolvedValue({ success: true })

    const actions = createMonitoringWatchlistActions()

    await actions.createWatchlist('趋势观察')
    await actions.addStock('101', '600519')
    await actions.removeStock('101', '600519')

    expect(apiClient.post).toHaveBeenNthCalledWith(1, '/v1/monitoring/watchlists', {
      name: '趋势观察',
      watchlist_type: 'manual',
    })
    expect(apiClient.post).toHaveBeenNthCalledWith(2, '/v1/monitoring/watchlists/101/stocks', {
      stock_code: '600519',
    })
    expect(apiClient.delete).toHaveBeenCalledWith('/v1/monitoring/watchlists/101/stocks/600519')
  })
})
