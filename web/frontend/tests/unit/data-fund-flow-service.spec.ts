import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  FUND_FLOW_PAGE_API_ROOT,
  fundFlowPageService
} from '@/api/services/fundFlowPageService'

const apiGetMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/apiClient', () => ({
  apiGet: apiGetMock
}))

describe('fundFlowPageService public contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('freezes the data/fund-flow public root at akshare market fund-flow', () => {
    expect(FUND_FLOW_PAGE_API_ROOT).toBe('/akshare/market/fund-flow')
  })

  it('loads the page snapshot through hsgt-summary and big-deal under the same root', async () => {
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        code: 200,
        message: 'ok',
        data: {
          data: [
            { date: '2026-03-09', north_money: 12.4, south_money: -8.2 },
            { date: '2026-03-10', north_money: 18.6, south_money: -3.1 },
            { date: '2026-03-11', north_money: 25.2, south_money: 4.8 }
          ]
        },
        timestamp: '2026-03-11T00:00:00Z',
        request_id: 'req-fund-flow-summary'
      })
      .mockResolvedValueOnce({
        success: true,
        code: 200,
        message: 'ok',
        data: {
          data: [
            {
              symbol: '600000',
              name: '浦发银行',
              big_deal_amount: 9800000,
              big_deal_buy_amount: 5300000,
              big_deal_sell_amount: 4500000,
              big_deal_net_inflow: 800000
            }
          ]
        },
        timestamp: '2026-03-11T00:00:00Z',
        request_id: 'req-fund-flow-ranking'
      })

    await fundFlowPageService.getFundFlowPageSnapshot({
      timeframe: '3day'
    })

    expect(apiGetMock).toHaveBeenCalledTimes(2)
    expect(apiGetMock.mock.calls[0][0]).toBe('/akshare/market/fund-flow/hsgt-summary')
    expect(apiGetMock.mock.calls[0][1]).toEqual({
      start_date: expect.any(String),
      end_date: expect.any(String)
    })
    expect(apiGetMock.mock.calls[1][0]).toBe('/akshare/market/fund-flow/big-deal')
  })
})
