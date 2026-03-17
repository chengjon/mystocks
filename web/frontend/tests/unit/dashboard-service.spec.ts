import { beforeEach, describe, expect, it, vi } from 'vitest'

import dashboardService, { DASHBOARD_REAL_API_ENDPOINTS } from '@/api/services/dashboardService'

const axiosGetMock = vi.hoisted(() => vi.fn())
const apiGetMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/apiClient', () => ({
  default: {
    get: axiosGetMock
  },
  apiGet: apiGetMock
}))

describe('dashboardService public contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('freezes the real dashboard endpoint manifest inside the dashboard aggregator service', () => {
    expect(DASHBOARD_REAL_API_ENDPOINTS).toEqual({
      marketOverview: '/dashboard/market-overview',
      fundFlow: '/akshare/market/fund-flow/hsgt-summary',
      industryFlow: '/v2/market/sector/fund-flow',
      stockFlowRanking: '/akshare/market/fund-flow/big-deal'
    })
    expect(Object.isFrozen(DASHBOARD_REAL_API_ENDPOINTS)).toBe(true)
  })

  it('uses the dashboard market-overview public path for the dashboard root object', async () => {
    apiGetMock.mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: {
        indices: [],
        up_count: 0,
        down_count: 0,
        flat_count: 0
      },
      timestamp: '2026-03-11T00:00:00Z',
      request_id: 'req-dashboard-service'
    })

    await dashboardService.getDashboardMarketOverview(6)

    expect(apiGetMock).toHaveBeenCalledWith('/dashboard/market-overview', { limit: 6 })
    expect(axiosGetMock).not.toHaveBeenCalled()
  })

  it('routes the dashboard fund-flow side panel through the shared API wrapper', async () => {
    apiGetMock.mockResolvedValue({
      data: {
        hgt: { amount: 0, change: 0 },
        sgt: { amount: 0, change: 0 },
        northTotal: { amount: 0, monthly: 0 },
        mainForce: { amount: 0, percentage: 0 }
      }
    })

    await dashboardService.getFundFlow('2026-03-11')

    expect(apiGetMock).toHaveBeenCalledWith('/akshare/market/fund-flow/hsgt-summary', {
      start_date: '2026-03-11',
      end_date: '2026-03-11'
    })
    expect(axiosGetMock).not.toHaveBeenCalled()
  })

  it('routes dashboard industry heat requests through the shared API wrapper', async () => {
    apiGetMock.mockResolvedValue({
      data: []
    })

    await dashboardService.getIndustryFlow('change_percent', 12)

    expect(apiGetMock).toHaveBeenCalledWith('/v2/market/sector/fund-flow', {
      sort: 'change_percent',
      limit: 12
    })
    expect(axiosGetMock).not.toHaveBeenCalled()
  })

  it('routes dashboard stock ranking requests through the shared API wrapper', async () => {
    apiGetMock.mockResolvedValue({
      data: []
    })

    await dashboardService.getStockFlowRanking('3day', 10)

    expect(apiGetMock).toHaveBeenCalledWith('/akshare/market/fund-flow/big-deal', {
      period: '3day',
      limit: 10
    })
    expect(axiosGetMock).not.toHaveBeenCalled()
  })
})
