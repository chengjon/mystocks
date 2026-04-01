import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getFundFlowMock,
  cacheGetMock,
  cacheSetMock,
  cacheClearMock,
  cacheStatsMock,
  adaptFundFlowMock,
  onMountedMock,
} = vi.hoisted(() => ({
  getFundFlowMock: vi.fn(),
  cacheGetMock: vi.fn(),
  cacheSetMock: vi.fn(),
  cacheClearMock: vi.fn(),
  cacheStatsMock: vi.fn(() => ({ size: 0, hits: 0, misses: 0 })),
  adaptFundFlowMock: vi.fn(),
  onMountedMock: vi.fn(),
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: onMountedMock,
  }
})

vi.mock('@/api/services/marketService', () => ({
  marketService: {
    getFundFlow: getFundFlowMock,
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

vi.mock('@/api/adapters/marketAdapter', () => ({
  MarketAdapter: {
    adaptFundFlow: adaptFundFlowMock,
  },
}))

import { useMarket } from '@/composables/useMarket'

describe('useMarket fund flow bridge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    cacheGetMock.mockReturnValue(undefined)
    getFundFlowMock.mockResolvedValue({
      success: true,
      data: {
        fund_flow: [
          {
            trade_date: '2026-04-01',
            super_large_net_inflow: 100,
            large_net_inflow: 50,
            medium_net_inflow: 25,
            small_net_inflow: 10,
          },
        ],
      },
    })
    adaptFundFlowMock.mockReturnValue([
      {
        date: '2026-04-01',
        timestamp: 1711929600000,
        main_force: { inflow: 100, outflow: 0, net_flow: 100, ratio: 0 },
        large_orders: { inflow: 50, outflow: 0, net_flow: 50, ratio: 0 },
        big_orders: { inflow: 25, outflow: 0, net_flow: 25, ratio: 0 },
        medium_orders: { inflow: 10, outflow: 0, net_flow: 10, ratio: 0 },
        small_orders: { inflow: 0, outflow: 0, net_flow: 0, ratio: 0 },
        total_inflow: 185,
        total_outflow: 0,
        total_net_flow: 185,
      },
    ])
  })

  it('fetches, adapts, and caches fund flow data through the market service', async () => {
    const market = useMarket({ autoFetch: false })

    await market.fetchFundFlow({ symbol: '000001.SZ', timeframe: '5' })

    expect(getFundFlowMock).toHaveBeenCalledWith({
      symbol: '000001.SZ',
      timeframe: '5',
    })
    expect(adaptFundFlowMock).toHaveBeenCalledWith({
      success: true,
      data: {
        fund_flow: [
          {
            trade_date: '2026-04-01',
            super_large_net_inflow: 100,
            large_net_inflow: 50,
            medium_net_inflow: 25,
            small_net_inflow: 10,
          },
        ],
      },
    })
    expect(cacheSetMock).toHaveBeenCalledWith(
      'market:fund_flow:{"symbol":"000001.SZ","timeframe":"5"}',
      [
        expect.objectContaining({
          date: '2026-04-01',
          total_net_flow: 185,
        }),
      ],
      { ttl: 600 },
    )
    expect(market.fundFlowData.value).toEqual([
      expect.objectContaining({
        date: '2026-04-01',
        total_net_flow: 185,
      }),
    ])
  })
})
