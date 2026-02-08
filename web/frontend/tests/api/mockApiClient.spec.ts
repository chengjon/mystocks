import { describe, it, expect, vi } from 'vitest'
import { mockApiClient } from '@/api/mockApiClient'

describe('mockApiClient', () => {
  it('should return market overview data', async () => {
    const response = await mockApiClient.get('/api/market/v2/etf/list')
    expect(response.success).toBe(true)
    expect(response.data).toHaveLength(4)
    expect(response.data[0]).toHaveProperty('symbol')
  })

  it('should return fund flow data', async () => {
    const response = await mockApiClient.get('/api/market/fund-flow')
    expect(response.success).toBe(true)
    expect(response.data).toHaveProperty('hgt')
    expect(response.data).toHaveProperty('sgt')
  })

  it('should return trend data for specific symbol', async () => {
    const response = await mockApiClient.get('/api/market/trend/000001.SH')
    expect(response.success).toBe(true)
    expect(response.data).toHaveProperty('symbol', '000001.SH')
    expect(response.data.data).toHaveLength(240)
  })

  it('should fallback to generic mock for unknown url', async () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const response = await mockApiClient.get('/api/unknown')
    expect(response.success).toBe(true)
    expect(response.data.url).toBe('/api/unknown')
    consoleSpy.mockRestore()
  })
})
