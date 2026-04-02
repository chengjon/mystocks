import { beforeEach, describe, expect, it, vi } from 'vitest'

const { putMock } = vi.hoisted(() => ({
  putMock: vi.fn(),
}))

vi.mock('@/api/user.ts', () => ({
  userApi: {},
}))

vi.mock('@/utils/request.ts', () => ({
  request: {
    put: putMock,
  },
}))

import { watchlistService } from '@/api/services/watchlistService.ts'

describe('watchlistService update watchlist route', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    putMock.mockResolvedValue({
      data: {
        success: true,
        data: {
          id: 7,
          name: '趋势跟踪池',
          watchlist_type: 'strategy',
          risk_profile: { risk_tolerance: 80 },
          is_active: false,
          stocks_count: 2,
        },
      },
    })
  })

  it('updates monitoring watchlists through the dedicated monitoring route instead of the generic user watchlist API', async () => {
    const response = await watchlistService.updateWatchlist(7, {
      name: '趋势跟踪池',
      watchlist_type: 'strategy',
      risk_profile: { risk_tolerance: 80 },
    })

    expect(putMock).toHaveBeenCalledWith('/api/v1/monitoring/watchlists/7', {
      name: '趋势跟踪池',
      watchlist_type: 'strategy',
      risk_profile: { risk_tolerance: 80 },
    })
    expect(response).toEqual({
      success: true,
      data: {
        id: 7,
        name: '趋势跟踪池',
        watchlist_type: 'strategy',
        risk_profile: { risk_tolerance: 80 },
        is_active: false,
        stocks_count: 2,
      },
      message: undefined,
    })
  })
})
