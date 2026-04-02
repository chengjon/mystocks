import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getWatchlistsMock } = vi.hoisted(() => ({
  getWatchlistsMock: vi.fn(),
}))

vi.mock('@/api/user.ts', () => ({
  userApi: {
    getWatchlists: getWatchlistsMock,
  },
}))

import { watchlistService } from '@/api/services/watchlistService.ts'

describe('watchlistService watchlist normalization', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getWatchlistsMock.mockResolvedValue([
      {
        id: '5',
        name: '高股息',
        statistics: {
          totalStocks: 3,
        },
        stocks: [],
      },
      {
        id: '6',
        name: '成长股',
        statistics: {
          totalStocks: 0,
        },
        stocks: [
          { symbol: '300750.SZ' },
          { symbol: '002594.SZ' },
        ],
      },
    ])
  })

  it('derives stocks_count from watchlist statistics or stock rows instead of defaulting to zero', async () => {
    const response = await watchlistService.listWatchlists()

    expect(getWatchlistsMock).toHaveBeenCalledTimes(1)
    expect(response).toEqual({
      success: true,
      data: [
        {
          id: 5,
          name: '高股息',
          watchlist_type: 'manual',
          risk_profile: {},
          stocks_count: 3,
        },
        {
          id: 6,
          name: '成长股',
          watchlist_type: 'manual',
          risk_profile: {},
          stocks_count: 2,
        },
      ],
    })
  })
})
