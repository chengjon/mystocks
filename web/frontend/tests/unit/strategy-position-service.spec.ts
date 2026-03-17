import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  STRATEGY_POSITION_API_ROOT,
  strategyPositionService
} from '@/api/services/strategyPositionService'

const apiGetMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/apiClient', () => ({
  apiGet: apiGetMock
}))

describe('strategyPositionService public contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('freezes the strategy/pos public root at v1 trade positions', () => {
    expect(STRATEGY_POSITION_API_ROOT).toBe('/v1/trade/positions')
  })

  it('loads and normalizes position exposure through the shared v1 trade positions root', async () => {
    apiGetMock.mockResolvedValue({
      positions: [
        {
          symbol: '600519',
          name: '贵州茅台',
          quantity: 100,
          average_cost: 1800,
          current_price: 1850,
          market_value: 185000,
          unrealized_pnl: 5000,
          weight: 0.35
        },
        {
          symbol: '000001',
          name: '平安银行',
          quantity: 500,
          average_cost: 12.5,
          current_price: 12.8,
          market_value: 6400,
          unrealized_pnl: 150,
          weight: 0.12
        }
      ],
      total_value: 191400,
      total: 2
    })

    const response = await strategyPositionService.getPositionExposure()

    expect(apiGetMock).toHaveBeenCalledWith('/v1/trade/positions')
    expect(response.success).toBe(true)
    expect(response.data.summary.positionsCount).toBe(2)
    expect(response.data.summary.totalMarketValue).toBe(191400)
    expect(response.data.summary.maxPositionPercent).toBe(35)
    expect(response.data.positions[0]).toMatchObject({
      symbol: '600519',
      name: '贵州茅台',
      quantity: 100,
      cost: 1800,
      price: 1850,
      pnl: 5000
    })
  })

  it('preserves upstream failure codes instead of collapsing them into a synthetic 500', async () => {
    apiGetMock.mockResolvedValue({
      success: false,
      code: 422,
      message: '参数非法',
      request_id: 'req-strategy-pos-invalid',
      process_time: '12.5',
      errors: { detail: 'invalid symbol' }
    })

    const response = await strategyPositionService.getPositionExposure()

    expect(response.success).toBe(false)
    expect(response.code).toBe(422)
    expect(response.message).toBe('参数非法')
    expect(response.request_id).toBe('req-strategy-pos-invalid')
    expect(response.process_time).toBe('12.5')
    expect(response.data).toEqual({
      summary: {
        totalMarketValue: 0,
        totalProfitLoss: 0,
        totalProfitLossPercent: 0,
        positionsCount: 0,
        maxPositionPercent: 0
      },
      positions: []
    })
  })
})
