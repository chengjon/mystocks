import { describe, it, expect, vi } from 'vitest'
import { marketService } from '@/api/services/marketService'
import apiClient from '@/api/apiClient'

// Mock apiClient
vi.mock('@/api/apiClient', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('marketService', () => {
  it('should fetch real-time quote', async () => {
    const mockData = { price: 100 }
    // @ts-ignore
    apiClient.get.mockResolvedValue({ data: mockData })

    const result = await marketService.getQuote('000001.SH')
    expect(apiClient.get).toHaveBeenCalledWith('/api/market/quote/000001.SH')
    expect(result).toEqual(mockData)
  })

  it('should fetch trend data', async () => {
    const mockData = { symbol: '000001.SH', data: [] }
    // @ts-ignore
    apiClient.get.mockResolvedValue({ data: mockData })

    const result = await marketService.getTrend('000001.SH')
    expect(apiClient.get).toHaveBeenCalledWith('/api/market/trend/000001.SH')
    expect(result).toEqual(mockData)
  })

  it('should fetch kline data', async () => {
    const mockData = [{ close: 100 }]
    // @ts-ignore
    apiClient.get.mockResolvedValue({ data: mockData })

    const result = await marketService.getKLine('000001.SH', '1d')
    expect(apiClient.get).toHaveBeenCalledWith('/api/market/kline', {
      params: { symbol: '000001.SH', period: '1d' }
    })
    expect(result.symbol).toBe('000001.SH')
    expect(result.data).toEqual(mockData)
  })
})
