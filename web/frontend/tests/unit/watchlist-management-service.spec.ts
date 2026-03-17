import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  WATCHLIST_MANAGEMENT_API_ROOT,
  watchlistService
} from '@/api/services/watchlistService'
import { apiDelete, apiGet, apiPost } from '@/api/apiClient'

const apiGetMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())
const apiDeleteMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/apiClient', () => ({
  apiGet: apiGetMock,
  apiPost: apiPostMock,
  apiDelete: apiDeleteMock
}))

describe('watchlistService public contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('freezes the watchlist public root at the v1 monitoring namespace', () => {
    expect(WATCHLIST_MANAGEMENT_API_ROOT).toBe('/v1/monitoring/watchlists')
  })

  it('loads watchlists through the shared v1 public root', async () => {
    apiGetMock.mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: [],
      timestamp: '2026-03-11T00:00:00Z',
      request_id: 'req-watchlist-list'
    })

    await watchlistService.listWatchlists()

    expect(apiGet).toHaveBeenCalledWith('/v1/monitoring/watchlists')
  })

  it('loads watchlist stocks through the nested public path', async () => {
    apiGetMock.mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: [],
      timestamp: '2026-03-11T00:00:00Z',
      request_id: 'req-watchlist-stocks'
    })

    await watchlistService.listWatchlistStocks(7)

    expect(apiGet).toHaveBeenCalledWith('/v1/monitoring/watchlists/7/stocks')
  })

  it('removes a stock by stock_code instead of local row id', async () => {
    apiDeleteMock.mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: null,
      timestamp: '2026-03-11T00:00:00Z',
      request_id: 'req-watchlist-remove'
    })

    await watchlistService.removeStockFromWatchlist(7, '000001.SZ')

    expect(apiDelete).toHaveBeenCalledWith('/v1/monitoring/watchlists/7/stocks/000001.SZ')
  })

  it('creates and adds stocks through the same public root', async () => {
    apiPostMock.mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: null,
      timestamp: '2026-03-11T00:00:00Z',
      request_id: 'req-watchlist-write'
    })

    await watchlistService.createWatchlist({
      name: 'My List',
      watchlist_type: 'manual',
      risk_profile: { risk_tolerance: 60 }
    })
    await watchlistService.addStockToWatchlist(7, {
      stock_code: '000001.SZ',
      weight: 0.1
    })

    expect(apiPost).toHaveBeenNthCalledWith(1, '/v1/monitoring/watchlists', {
      name: 'My List',
      watchlist_type: 'manual',
      risk_profile: { risk_tolerance: 60 }
    })
    expect(apiPost).toHaveBeenNthCalledWith(2, '/v1/monitoring/watchlists/7/stocks', {
      stock_code: '000001.SZ',
      weight: 0.1
    })
  })
})
