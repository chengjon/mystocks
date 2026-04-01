/**
 * Market API legacy compatibility tests
 *
 * Verifies the deprecated wrapper delegates to the modern market service
 * without requiring a live backend.
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

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

  it('does not rely on ts-nocheck in the legacy compatibility layer', () => {
    const source = readFileSync(resolve(process.cwd(), 'src/api/marketWithFallback.ts'), 'utf8')
    const forbiddenDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(forbiddenDirective)
  })

  it('delegates fund flow requests using the modern parameter names', async () => {
    const fundFlow = [{ date: '2026-03-31', netInflow: 12.5 }]
    getFundFlowMock.mockResolvedValueOnce(fundFlow)

    await expect(
      marketApiService.getFundFlow({
        startDate: '2026-03-01',
        endDate: '2026-03-31',
        market: 'sz'
      })
    ).resolves.toEqual(fundFlow)

    expect(getFundFlowMock).toHaveBeenCalledWith({
      startDate: '2026-03-01',
      endDate: '2026-03-31',
      market: 'sz'
    })
  })

  it('falls back unsupported legacy kline intervals to 1d with modern field names', async () => {
    const kline = {
      categoryData: ['2026-03-31'],
      values: [[1, 2, 0.5, 2.5]],
      volumes: [1000]
    }
    getKLineDataMock.mockResolvedValueOnce(kline)

    await expect(
      marketApiService.getKLineData({
        symbol: '000001.SZ',
        interval: '4h',
        startDate: '2026-03-01',
        endDate: '2026-03-31',
        limit: 50
      })
    ).resolves.toEqual(kline)

    expect(getKLineDataMock).toHaveBeenCalledWith({
      symbol: '000001.SZ',
      interval: '1d',
      startDate: '2026-03-01',
      endDate: '2026-03-31',
      limit: 50
    })
  })
})
