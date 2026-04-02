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

describe('watchlistService watchlist normalization', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getMock.mockResolvedValue({
      data: {
        success: true,
        data: [
          {
            id: '5',
            name: '高股息',
            watchlist_type: 'manual',
            risk_profile: {},
            stocks_count: 3,
          },
          {
            id: '6',
            name: '成长股',
            watchlist_type: 'strategy',
            risk_profile: {
              risk_tolerance: 80,
            },
            stocks_count: 2,
          },
        ],
      },
    })
  })

  it('loads watchlists from the monitoring route instead of the generic user watchlist API', async () => {
    const response = await watchlistService.listWatchlists()

    expect(getMock).toHaveBeenCalledWith('/api/v1/monitoring/watchlists')
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
          watchlist_type: 'strategy',
          risk_profile: { risk_tolerance: 80 },
          stocks_count: 2,
        },
      ],
      message: undefined,
    })
  })
})
