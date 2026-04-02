import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getWatchlistMock } = vi.hoisted(() => ({
  getWatchlistMock: vi.fn(),
}))

vi.mock('@/api/user.ts', () => ({
  userApi: {
    getWatchlist: getWatchlistMock,
  },
}))

import { watchlistService } from '@/api/services/watchlistService.ts'

describe('watchlistService stock bridge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getWatchlistMock.mockResolvedValue({
      id: '7',
      name: '核心观察',
      isDefault: false,
      isPublic: false,
      owner: {
        userId: 'user-1',
        username: 'tester',
        displayName: 'Tester',
      },
      stocks: [
        {
          symbol: '600519.SH',
          name: '贵州茅台',
          market: 'A',
          currentPrice: 1800.5,
          changeAmount: 12.3,
          changePercent: '0.69%',
          volume: 1000,
          marketCap: 1,
          addedAt: '2026-04-02 09:30:00',
          notes: '白酒龙头',
          alerts: [
            {
              id: 'alert-1',
              type: 'price',
              condition: 'above',
              value: 1900,
              isActive: true,
              notificationMethod: 'push',
            },
            {
              id: 'alert-2',
              type: 'price',
              condition: 'below',
              value: 1600,
              isActive: false,
              notificationMethod: 'push',
            },
            {
              id: 'alert-3',
              type: 'volume',
              condition: 'above',
              value: 1000000,
              isActive: true,
              notificationMethod: 'push',
            },
          ],
          customFields: {
            entry_price: 1680,
            stop_loss_price: 1550,
            target_price: 1950,
            weight: 0.35,
          },
        },
        {
          symbol: '000001.SZ',
          name: '平安银行',
          market: 'A',
          currentPrice: 12.34,
          changeAmount: -0.08,
          changePercent: '-0.64%',
          volume: 2000,
          marketCap: 1,
          addedAt: '2026-04-02 09:35:00',
          alerts: [
            {
              id: 'alert-4',
              type: 'price',
              condition: 'below',
              value: 11.5,
              isActive: true,
              notificationMethod: 'push',
            },
          ],
        },
      ],
      statistics: {
        totalStocks: 2,
        totalValue: 0,
        todayChange: 0,
        todayChangePercent: '0%',
        bestPerformer: {
          symbol: '600519.SH',
          name: '贵州茅台',
          changePercent: '0.69%',
        },
        worstPerformer: {
          symbol: '000001.SZ',
          name: '平安银行',
          changePercent: '-0.64%',
        },
        sectors: [],
      },
      tags: [],
      createdAt: '2026-04-01 09:00:00',
      updatedAt: '2026-04-02 09:00:00',
      sortOrder: 0,
    })
  })

  it('maps watchlist detail stocks into monitoring records instead of returning an empty placeholder list', async () => {
    const response = await watchlistService.listWatchlistStocks(7)

    expect(getWatchlistMock).toHaveBeenCalledWith('7')
    expect(response).toEqual({
      success: true,
      data: [
        {
          id: 1,
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
          id: 2,
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
    })
  })
})
