import { beforeEach, describe, expect, it, vi } from 'vitest'

import { marketService } from '@/api/services/marketService'
import { apiGet } from '@/api/apiClient'

const apiGetMock = vi.hoisted(() => vi.fn())
const apiClientGetMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/apiClient', () => ({
  apiGet: apiGetMock,
  apiClient: {
    get: apiClientGetMock
  }
}))

describe('marketService data concept contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('uses the v2 sector fund-flow public path for concept analysis', async () => {
    apiGetMock.mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: [],
      timestamp: '2026-03-11T00:00:00Z',
      request_id: 'req-data-concept'
    })

    await marketService.getConceptFundFlow({
      timeframe: '今日',
      limit: 8
    })

    expect(apiGet).toHaveBeenCalledWith('/v2/market/sector/fund-flow', {
      sector_type: '概念',
      timeframe: '今日',
      limit: 8
    })
  })
})
