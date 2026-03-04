import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from '../../apiClient'
import { dashboardService } from '../dashboardService'

vi.mock('../../apiClient', () => ({
  default: {
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
