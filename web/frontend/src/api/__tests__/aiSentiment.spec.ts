import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiClient } from '@/api/apiClient.ts'
import request from '@/utils/request.ts'

import {
  analyzeSentiment,
  getMarketSentiment,
  getSentimentNews,
  getStockSentiment,
} from '../aiSentiment'

vi.mock('@/utils/request.ts', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

vi.mock('@/api/apiClient.ts', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('aiSentiment API client', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
    vi.mocked(request.get).mockReset()
    vi.mocked(request.post).mockReset()
  })

  it('calls canonical v1 sentiment endpoints from the OpenAPI contract', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ success: true, code: 200, data: {} } as never)
    vi.mocked(apiClient.post).mockResolvedValue({ success: true, code: 200, data: {} } as never)
    vi.mocked(request.get).mockResolvedValue({ data: { success: true, code: 200, data: {} } } as never)
    vi.mocked(request.post).mockResolvedValue({ data: { success: true, code: 200, data: {} } } as never)

    await getSentimentNews({ page: 1, page_size: 50 })
    await getMarketSentiment()
    await getStockSentiment('600519', 7)
    await analyzeSentiment({
      symbol: '600519',
      text: '公司增长恢复，市场看好',
      source: 'ai-workbench',
    })

    expect(apiClient.get).toHaveBeenCalledWith('/announcement/list', { params: { page: 1, page_size: 50 } })
    expect(apiClient.get).toHaveBeenCalledWith('/v1/sentiment/market')
    expect(apiClient.get).toHaveBeenCalledWith('/v1/sentiment/stock/600519', { params: { days: 7 } })
    expect(apiClient.post).toHaveBeenCalledWith(
      '/v1/sentiment/analyze',
      expect.objectContaining({ symbol: '600519' }),
    )
    expect(request.get).not.toHaveBeenCalled()
    expect(request.post).not.toHaveBeenCalled()
  })
})
