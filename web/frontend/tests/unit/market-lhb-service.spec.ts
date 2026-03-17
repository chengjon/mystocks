import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  MARKET_DRAGON_TIGER_API_ROOT,
  dragonTigerService
} from '@/api/services/dragonTigerService'

const apiClientGetMock = vi.hoisted(() => vi.fn())

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: apiClientGetMock
  }
}))

describe('dragonTigerService public contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('freezes the market lhb public root at the v1 market namespace', () => {
    expect(MARKET_DRAGON_TIGER_API_ROOT).toBe('/v1/market/lhb')
  })

  it('loads dragon tiger rows through the shared v1 market root', async () => {
    apiClientGetMock.mockResolvedValue([])

    await dragonTigerService.listDragonTiger({
      tradeDate: '2026-03-11',
      limit: 12
    })

    expect(apiClientGetMock).toHaveBeenCalledWith('/v1/market/lhb', {
      params: {
        start_date: '2026-03-11',
        end_date: '2026-03-11',
        limit: 12
      }
    })
  })
})
