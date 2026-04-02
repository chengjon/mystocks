import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
}))

vi.mock('@/api/user.ts', () => ({
  userApi: {},
}))

vi.mock('@/utils/request.ts', () => ({
  request: {
    get: getMock,
  },
}))

import { watchlistService } from '@/api/services/watchlistService.ts'

describe('watchlistService stock bridge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getMock
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: [
            {
              id: 301,
              watchlist_id: 7,
              stock_code: '600519.SH',
              entry_price: 1680,
              entry_reason: '白酒龙头',
              stop_loss_price: 1550,
              target_price: 1950,
              weight: 0.35,
              is_active: true,
            },
            {
              id: 302,
              watchlist_id: 7,
              stock_code: '000001.SZ',
              is_active: true,
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: [
            {
              level: 'warning',
              type: 'stop_loss',
              stock_code: '600519.SH',
              message: '触及止损线',
              details: {},
            },
            {
              level: 'info',
              type: 'rebalance',
              stock_code: '600519.SH',
              message: '建议调仓',
              details: {},
            },
            {
              level: 'warning',
              type: 'stop_loss',
              stock_code: '000001.SZ',
              message: '关注支撑位',
              details: {},
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          success: true,
          data: {
            quotes: [
              {
                symbol: '600519.SH',
                name: '贵州茅台',
                current_price: 1800.5,
              },
              {
                symbol: '000001.SZ',
                name: '平安银行',
                current_price: 12.34,
              },
            ],
          },
        },
      })
  })

  it('merges monitoring stock rows with portfolio alerts and quotes instead of reading the generic user watchlist detail API', async () => {
    const response = await watchlistService.listWatchlistStocks(7)

    expect(getMock).toHaveBeenNthCalledWith(1, '/api/v1/monitoring/watchlists/7/stocks')
    expect(getMock).toHaveBeenNthCalledWith(2, '/api/v1/monitoring/analysis/portfolio/7/alerts')
    expect(getMock).toHaveBeenNthCalledWith(3, '/api/v1/market/quotes', {
      params: {
        symbols: '600519.SH,000001.SZ',
      },
    })
    expect(response).toEqual({
      success: true,
      data: [
        {
          id: 301,
          stock_code: '600519.SH',
          entry_price: 1680,
          current_price: 1800.5,
          entry_reason: '白酒龙头',
          stop_loss_price: 1550,
          target_price: 1950,
          weight: 0.35,
          alerts_count: 2,
        },
        {
          id: 302,
          stock_code: '000001.SZ',
          entry_price: undefined,
          current_price: 12.34,
          entry_reason: null,
          stop_loss_price: undefined,
          target_price: undefined,
          weight: undefined,
          alerts_count: 1,
        },
      ],
      message: undefined,
    })
  })
})
