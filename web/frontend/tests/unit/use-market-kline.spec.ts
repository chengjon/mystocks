import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getKlineMock,
  cacheGetMock,
  cacheSetMock,
  cacheClearMock,
  cacheStatsMock,
  adaptKLineDataMock,
  onMountedMock,
} = vi.hoisted(() => ({
  getKlineMock: vi.fn(),
  cacheGetMock: vi.fn(),
  cacheSetMock: vi.fn(),
  cacheClearMock: vi.fn(),
  cacheStatsMock: vi.fn(() => ({ size: 0, hits: 0, misses: 0 })),
  adaptKLineDataMock: vi.fn(),
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
    getKline: getKlineMock,
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
    adaptKLineData: adaptKLineDataMock,
  },
}))

import { useMarket } from '@/composables/useMarket'

describe('useMarket kline bridge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    cacheGetMock.mockReturnValue(undefined)
    getKlineMock.mockResolvedValue({
      success: true,
      data: {
        symbol: '000001.SZ',
        period: '1d',
        data: [
          {
            datetime: '2026-04-01',
            open: 10,
            high: 12,
            low: 9,
            close: 11,
            volume: 1000,
          },
        ],
      },
    })
    adaptKLineDataMock.mockReturnValue({
      categoryData: ['2026-04-01'],
      values: [
        {
          open: 10,
          close: 11,
          low: 9,
          high: 12,
          volume: 1000,
        },
      ],
      volumes: [1000],
    })
  })

  it('fetches, adapts, and caches kline data through the market service', async () => {
    const market = useMarket({ autoFetch: false })

    await market.fetchKLineData({
      symbol: '000001.SZ',
      interval: '1d',
      startDate: '2026-04-01',
      endDate: '2026-04-10',
      limit: 50,
    })

    expect(getKlineMock).toHaveBeenCalledWith({
      stock_code: '000001.SZ',
      period: '1d',
    })
    expect(adaptKLineDataMock).toHaveBeenCalledWith({
      success: true,
      data: {
        symbol: '000001.SZ',
        period: '1d',
        data: [
          {
            datetime: '2026-04-01',
            open: 10,
            high: 12,
            low: 9,
            close: 11,
            volume: 1000,
          },
        ],
      },
    })
    expect(cacheSetMock).toHaveBeenCalledWith(
      'market:kline:000001.SZ:1d',
      [
        {
          timestamp: '2026-04-01',
          date: '2026-04-01',
          open: 10,
          close: 11,
          low: 9,
          high: 12,
          volume: 1000,
          amount: 1000,
          symbol: '000001.SZ',
          interval: '1d',
        },
      ],
      { ttl: 180 },
    )
    expect(market.klineData.value).toEqual([
      {
        timestamp: '2026-04-01',
        date: '2026-04-01',
        open: 10,
        close: 11,
        low: 9,
        high: 12,
        volume: 1000,
        amount: 1000,
        symbol: '000001.SZ',
        interval: '1d',
      },
    ])
  })
})
