import { beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '../../apiClient'
import { dashboardService } from '../dashboardService'

vi.mock('../../apiClient', () => ({
  apiClient: {
    get: vi.fn()
  }
}))

describe('dashboardService.getFundFlow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.get).mockResolvedValue({ data: { data: {} } } as never)
  })

  it('sends start_date and end_date when date is omitted', async () => {
    await dashboardService.getFundFlow()

    expect(apiClient.get).toHaveBeenCalledWith(
      '/akshare/market/fund-flow/hsgt-summary',
      expect.objectContaining({
        params: expect.objectContaining({
          start_date: expect.any(String),
          end_date: expect.any(String)
        })
      })
    )
  })

  it('maps provided date to both start_date and end_date', async () => {
    await dashboardService.getFundFlow('2026-03-03')

    expect(apiClient.get).toHaveBeenCalledWith('/akshare/market/fund-flow/hsgt-summary', {
      params: {
        start_date: '2026-03-03',
        end_date: '2026-03-03'
      }
    })
  })
})

describe('dashboardService.getTechnicalIndicatorsSafe', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns ok when all symbols resolve', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: { data: { name: 'RSI', value: 55, signal: 'buy', signalType: 'rise' } }
    } as never)

    const result = await dashboardService.getTechnicalIndicatorsSafe(['000001.SZ'], ['RSI'])

    expect(result.ok).toBe(true)
    expect(result.data['000001.SZ']).toHaveLength(1)
    expect(result.error).toBeUndefined()
  })

  it('accepts a top-level indicator payload from the unified endpoint', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: { name: 'RSI', value: 61.2, signal: '偏强', trend: 'rise' }
    } as never)

    const result = await dashboardService.getTechnicalIndicatorsSafe(['000001.SZ'], ['RSI'])

    expect(result.ok).toBe(true)
    expect(result.data['000001.SZ']).toEqual([
      { name: 'RSI', value: 61.2, signal: '偏强', trend: 'rise' }
    ])
    expect(result.error).toBeUndefined()
  })

  it('collects errors without throwing', async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error('network down'))

    const result = await dashboardService.getTechnicalIndicatorsSafe(['000001.SZ'], ['RSI'])

    expect(result.ok).toBe(false)
    expect(result.data).toEqual({})
    expect(result.error).toContain('network down')
  })

  it('preserves unified error-envelope messages instead of collapsing them into empty response', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      success: false,
      message: 'indicators detail 000001 unavailable',
      request_id: 'indicators-detail-fail',
      data: null,
    } as never)

    const result = await dashboardService.getTechnicalIndicatorsSafe(['000001'], ['RSI'])

    expect(result.ok).toBe(false)
    expect(result.data).toEqual({})
    expect(result.error).toContain('indicators detail 000001 unavailable')
    expect(result.error).not.toContain('empty response')
  })
})

describe('dashboardService.getStockFlowRanking', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('throws when the API client resolves a unified error envelope', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      success: false,
      message: 'stock flow ranking unavailable',
      request_id: 'dashboard-ranking-fail',
      data: null,
    } as never)

    await expect(dashboardService.getStockFlowRanking('1day', 10)).rejects.toThrow('stock flow ranking unavailable')
  })
})

describe('dashboardService.getSystemHealth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('throws when the API client resolves a unified error envelope', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      success: false,
      message: 'system health unavailable',
      request_id: 'dashboard-health-fail',
      data: null,
    } as never)

    await expect(dashboardService.getSystemHealth()).rejects.toThrow('system health unavailable')
  })
})
