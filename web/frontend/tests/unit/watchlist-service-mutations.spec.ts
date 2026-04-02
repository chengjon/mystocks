import { beforeEach, describe, expect, it, vi } from 'vitest'

const { postMock, deleteMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
  deleteMock: vi.fn(),
}))

vi.mock('@/api/user.ts', () => ({
  userApi: {},
}))

vi.mock('@/utils/request.ts', () => ({
  request: {
    post: postMock,
    delete: deleteMock,
  },
}))

import { watchlistService } from '@/api/services/watchlistService.ts'

describe('watchlistService monitoring mutations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates watchlists through the monitoring route', async () => {
    postMock.mockResolvedValueOnce({
      data: {
        success: true,
        data: {
          id: 9,
          name: '趋势自选',
          watchlist_type: 'strategy',
          risk_profile: { risk_tolerance: 70 },
          stocks_count: 0,
        },
        message: '创建清单成功',
      },
    })

    const response = await watchlistService.createWatchlist({
      name: '趋势自选',
      watchlist_type: 'strategy',
      risk_profile: { risk_tolerance: 70 },
    })

    expect(postMock).toHaveBeenCalledWith('/api/v1/monitoring/watchlists', {
      name: '趋势自选',
      watchlist_type: 'strategy',
      risk_profile: { risk_tolerance: 70 },
    })
    expect(response).toEqual({
      success: true,
      data: {
        id: 9,
        name: '趋势自选',
        watchlist_type: 'strategy',
        risk_profile: { risk_tolerance: 70 },
        stocks_count: 0,
      },
      message: '创建清单成功',
    })
  })

  it('adds and removes stocks through the monitoring routes', async () => {
    postMock.mockResolvedValueOnce({
      data: {
        success: true,
        data: {
          id: 1001,
          watchlist_id: 9,
          stock_code: '600519.SH',
        },
        message: '添加股票成功',
      },
    })
    deleteMock.mockResolvedValueOnce({
      data: {
        success: true,
        message: '移除股票成功',
      },
    })

    const addResponse = await watchlistService.addStockToWatchlist(9, {
      stock_code: '600519.SH',
      entry_price: 1680,
      entry_reason: '白酒龙头',
      stop_loss_price: 1550,
      target_price: 1950,
      weight: 0.35,
    })
    const removeResponse = await watchlistService.removeStockFromWatchlist(9, '600519.SH')

    expect(postMock).toHaveBeenCalledWith('/api/v1/monitoring/watchlists/9/stocks', {
      stock_code: '600519.SH',
      entry_price: 1680,
      entry_reason: '白酒龙头',
      stop_loss_price: 1550,
      target_price: 1950,
      weight: 0.35,
    })
    expect(deleteMock).toHaveBeenCalledWith('/api/v1/monitoring/watchlists/9/stocks/600519.SH')
    expect(addResponse).toEqual({
      success: true,
      data: null,
      message: '添加股票成功',
    })
    expect(removeResponse).toEqual({
      success: true,
      data: null,
      message: '移除股票成功',
    })
  })

  it('deletes watchlists through the monitoring route', async () => {
    deleteMock.mockResolvedValueOnce({
      data: {
        success: true,
        message: '删除清单成功',
      },
    })

    const response = await watchlistService.deleteWatchlist(9)

    expect(deleteMock).toHaveBeenCalledWith('/api/v1/monitoring/watchlists/9')
    expect(response).toEqual({
      success: true,
      data: null,
      message: '删除清单成功',
    })
  })
})
