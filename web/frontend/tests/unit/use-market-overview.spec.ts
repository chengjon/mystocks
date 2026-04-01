import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getMarketOverviewMock,
  cacheGetMock,
  cacheSetMock,
  cacheClearMock,
  cacheStatsMock,
  onMountedMock,
} = vi.hoisted(() => ({
  getMarketOverviewMock: vi.fn(),
  cacheGetMock: vi.fn(),
  cacheSetMock: vi.fn(),
  cacheClearMock: vi.fn(),
  cacheStatsMock: vi.fn(() => ({ size: 0, hits: 0, misses: 0 })),
  onMountedMock: vi.fn(),
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: onMountedMock,
  }
})

vi.mock('@/api/market', () => ({
  marketApi: {
    getMarketOverview: getMarketOverviewMock,
  },
}))

vi.mock('@/utils/cache/part-1', () => ({
  getCache: () => ({
    get: cacheGetMock,
    set: cacheSetMock,
    clear: cacheClearMock,
    getStats: cacheStatsMock,
  }),
}))

import { useMarket } from '@/composables/useMarket'

describe('useMarket market overview bridge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    cacheGetMock.mockReturnValue(undefined)
    getMarketOverviewMock.mockResolvedValue({
      market_status: 'bull',
      market_phase: 'markup',
      indices: {
        shanghai: {
          code: 'SH000001',
          name: '上证指数',
          current_price: 3100,
          change_amount: 12,
          change_percent: 0.39,
          volume: 100,
          amount: 200,
          open: 3080,
          high: 3110,
          low: 3070,
          close: 3100,
          prev_close: 3088,
        },
        shenzhen: {
          code: 'SZ399001',
          name: '深证成指',
          current_price: 9800,
          change_amount: 40,
          change_percent: 0.41,
          volume: 100,
          amount: 200,
          open: 9750,
          high: 9820,
          low: 9730,
          close: 9800,
          prev_close: 9760,
        },
        chiNext: {
          code: 'SZ399006',
          name: '创业板指',
          current_price: 2000,
          change_amount: 10,
          change_percent: 0.5,
          volume: 100,
          amount: 200,
          open: 1988,
          high: 2010,
          low: 1980,
          close: 2000,
          prev_close: 1990,
        },
      },
      sentiment: {
        advance_decline_ratio: 1.2,
        up_down_volume_ratio: 1.1,
        new_highs_new_lows_ratio: 1.05,
      },
      turnover: { total: 1, shanghai: 0.4, shenzhen: 0.6 },
      price_distribution: { up: 10, down: 5, flat: 2 },
      sector_performance: [],
      hot_concepts: [],
      capital_flow: { main_net: 1, retail_net: -1, institution_net: 2 },
      top_gainers: [],
      top_losers: [],
      technical_summary: { trend: 'bullish', support: 3000, resistance: 3200 },
      last_update: '2026-04-01T00:00:00Z',
      market_session: 'open',
      timestamp: '2026-04-01T00:00:00Z',
    })
  })

  it('fetches and caches market overview through marketApi instead of placeholder data', async () => {
    const market = useMarket({ autoFetch: false })

    await market.fetchMarketOverview()

    expect(getMarketOverviewMock).toHaveBeenCalledTimes(1)
    expect(cacheSetMock).toHaveBeenCalledWith(
      'market:overview',
      expect.objectContaining({
        market_status: 'bull',
        market_phase: 'markup',
      }),
      { ttl: 300 },
    )
    expect(market.marketOverview.value).toEqual(
      expect.objectContaining({
        market_status: 'bull',
        market_phase: 'markup',
      }),
    )
  })
})
