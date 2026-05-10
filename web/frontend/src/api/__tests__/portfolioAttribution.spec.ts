import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiClient } from '../apiClient'
import { getBacktestAttribution, getPositionAttribution } from '../portfolioAttribution.ts'

vi.mock('../apiClient', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

describe('portfolioAttribution API client', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.get).mockResolvedValue({ success: true, code: 200, data: {} } as never)
  })

  it('calls canonical v1 attribution endpoints', async () => {
    await getPositionAttribution()
    await getPositionAttribution({ date: '2026-05-08', sessionId: 'session_abc' })
    await getBacktestAttribution(42)

    expect(apiClient.get).toHaveBeenCalledWith('/v1/positions/attribution', { params: {} })
    expect(apiClient.get).toHaveBeenCalledWith('/v1/positions/attribution', {
      params: {
        date: '2026-05-08',
        session_id: 'session_abc',
      },
    })
    expect(apiClient.get).toHaveBeenCalledWith('/v1/backtest/42/attribution')
  })
})
