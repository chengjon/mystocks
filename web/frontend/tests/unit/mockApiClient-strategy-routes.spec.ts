import { describe, expect, it } from 'vitest'
import { mockApiClient } from '@/api/mockApiClient'

describe('mockApiClient strategy routes', () => {
  it('serves strategy list from the real endpoint family in explicit mock mode', async () => {
    const response = await mockApiClient.get('/v1/strategy/strategies', {
      params: { status: 'active' }
    })

    expect(response.success).toBe(true)
    expect(response.data.items.length).toBeGreaterThan(0)
    expect(response.data.items.every((item: { status: string }) => item.status === 'active')).toBe(true)
  })

  it('serves strategy detail from the real endpoint family in explicit mock mode', async () => {
    const response = await mockApiClient.get('/v1/strategy/strategies/1')

    expect(response.success).toBe(true)
    expect(response.data.id).toBe('1')
    expect(response.data.name).toBeTruthy()
  })
})
