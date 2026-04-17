import { beforeEach, describe, expect, it, vi } from 'vitest'

const { apiGetMock, apiPostMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn(),
  apiPostMock: vi.fn(),
}))

vi.mock('../../../src/api/apiClient.ts', () => ({
  apiClient: {
    get: apiGetMock,
    post: apiPostMock,
  },
}))

import { kronosApi } from '../../../src/api/kronos'

describe('kronosApi', () => {
  beforeEach(() => {
    apiGetMock.mockReset().mockResolvedValue({})
    apiPostMock.mockReset().mockResolvedValue({})
  })

  it('posts predict requests to the canonical Kronos endpoint', async () => {
    const payload = {
      model: 'small' as const,
      symbol: '600519',
      start_date: '2026-04-01',
      end_date: '2026-04-17',
      pred_len: 10,
      sample_count: 1,
      top_p: 0.9,
      temperature: 1.0,
    }

    await kronosApi.predict(payload)

    expect(apiPostMock).toHaveBeenCalledWith('/v1/kronos/predict', payload)
  })

  it('posts encode requests to the canonical Kronos endpoint', async () => {
    const payload = {
      model: 'small' as const,
      symbol: '000001',
      lookback: 120,
    }

    await kronosApi.encode(payload)

    expect(apiPostMock).toHaveBeenCalledWith('/v1/kronos/encode', payload)
  })

  it('fetches runtime status from the canonical Kronos endpoint', async () => {
    await kronosApi.getStatus()

    expect(apiGetMock).toHaveBeenCalledWith('/v1/kronos/status')
  })
})
