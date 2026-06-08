import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const { indexedDBMock, tradingApiManagerMock } = vi.hoisted(() => ({
  indexedDBMock: {
    getCache: vi.fn(),
    getStaleCache: vi.fn(),
    setCache: vi.fn(),
    getAllMarketData: vi.fn(),
    saveMarketData: vi.fn(),
    saveTechnicalIndicator: vi.fn(),
    clearAllData: vi.fn(),
    getStats: vi.fn(),
  },
  tradingApiManagerMock: {
    getMarketOverview: vi.fn(),
  },
}))

vi.mock('@/utils/indexedDB', () => ({
  indexedDB: indexedDBMock,
}))

vi.mock('@/services/TradingApiManager', () => ({
  tradingApiManager: tradingApiManagerMock,
}))

vi.mock('@/utils/workersManager/index', () => ({
  workersManager: {
    calculateIndicator: vi.fn(),
  },
}))

import { useMarketDataStore } from '@/stores/marketData'
import type { MarketOverview } from '@/services/TradingApiManager'

describe('useMarketDataStore cache fallback', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setActivePinia(createPinia())
    vi.clearAllMocks()
    Object.defineProperty(window.navigator, 'onLine', {
      configurable: true,
      value: true,
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('uses a valid indexedDB market overview cache without a network request', async () => {
    const cachedOverview: MarketOverview = {
      indices: [{ code: '000001', name: 'SSE Composite' }],
      rankings: [],
      volume: { amount: 1000 },
      lastUpdate: '2026-06-08 09:30:00',
    }

    indexedDBMock.getCache.mockResolvedValueOnce(cachedOverview)

    const store = useMarketDataStore()
    await store.loadMarketOverview()

    expect(indexedDBMock.getCache).toHaveBeenCalledWith('market_overview')
    expect(tradingApiManagerMock.getMarketOverview).not.toHaveBeenCalled()
    expect(store.state.marketOverview).toEqual(cachedOverview)
    expect(store.state.cacheMetadata).toMatchObject({
      isStale: false,
      source: 'indexeddb',
    })
    expect(store.state.syncStatus).toBe('idle')
  })

  it('uses explicit stale cache when market overview refresh fails', async () => {
    vi.spyOn(console, 'warn').mockImplementation(() => {})

    const staleOverview: MarketOverview = {
      indices: [],
      rankings: [],
      volume: { amount: 123456 },
      lastUpdate: '2026-06-08 09:31:00',
    }

    tradingApiManagerMock.getMarketOverview.mockRejectedValueOnce(new Error('overview unavailable'))
    indexedDBMock.getStaleCache.mockResolvedValueOnce(staleOverview)

    const store = useMarketDataStore()
    await store.loadMarketOverview(true)

    expect(tradingApiManagerMock.getMarketOverview).toHaveBeenCalledTimes(1)
    expect(indexedDBMock.getCache).not.toHaveBeenCalledWith('market_overview')
    expect(indexedDBMock.getStaleCache).toHaveBeenCalledWith('market_overview')
    expect(store.state.marketOverview).toEqual(staleOverview)
    expect(store.state.cacheMetadata).toMatchObject({
      isStale: true,
      source: 'cache',
    })
    expect(store.state.syncStatus).toBe('idle')
  })
})
