/**
 * Market API legacy compatibility tests
 *
 * Verifies the deprecated wrapper delegates to the modern market service
 * without requiring a live backend.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getMarketOverviewMock,
  getFundFlowMock,
  getKLineDataMock
} = vi.hoisted(() => ({
  getMarketOverviewMock: vi.fn(),
  getFundFlowMock: vi.fn(),
  getKLineDataMock: vi.fn()
}))

vi.mock('../market.ts', () => ({
  default: class MockMarketApiService {
    getMarketOverview = getMarketOverviewMock
    getFundFlow = getFundFlowMock
    getKLineData = getKLineDataMock
  }
}))

import { marketApiService } from '../marketWithFallback'

describe('Market API legacy compatibility layer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('delegates market overview requests to the modern market service', async () => {
    const overview = {
      marketStats: {
        totalStocks: 5300
      },
      topEtfs: []
    }

    getMarketOverviewMock.mockResolvedValueOnce(overview)

    await expect(marketApiService.getMarketOverview()).resolves.toEqual(overview)
    expect(getMarketOverviewMock).toHaveBeenCalledTimes(1)
  })

  it('delegates force refresh requests without changing the response shape', async () => {
    const overview = {
      marketStats: {
        totalStocks: 5200
      },
      topEtfs: [{ symbol: '510300' }]
    }

    getMarketOverviewMock.mockResolvedValueOnce(overview)

    await expect(marketApiService.getMarketOverview(true)).resolves.toEqual(overview)
    expect(getMarketOverviewMock).toHaveBeenCalledTimes(1)
  })

  it('exposes no-op cache management for backward compatibility', () => {
    marketApiService.clearCache()

    expect(marketApiService.getCacheStats()).toEqual({
      size: 0,
      hits: 0,
      misses: 0
    })
  })

  it('keeps the deprecated market API surface available', () => {
    expect(marketApiService.getMarketOverview).toBeDefined()
    expect(marketApiService.getFundFlow).toBeDefined()
    expect(marketApiService.getKLineData).toBeDefined()
  })
})
