import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useStrategyStore } from '@/stores/strategy'

vi.mock('@/services/TradingApiManager', () => ({
  tradingApiManager: {
    getStrategyManagement: vi.fn()
  }
}))

import { tradingApiManager } from '@/services/TradingApiManager'

const mockTradingApiManager = vi.mocked(tradingApiManager)

describe('useStrategyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('loads strategy management through the standardized API store path', async () => {
    mockTradingApiManager.getStrategyManagement.mockResolvedValue({
      strategies: [{ id: 's1' }],
      templates: [{ id: 't1' }]
    })

    const store = useStrategyStore()
    await store.loadStrategyManagement()

    expect(mockTradingApiManager.getStrategyManagement).toHaveBeenCalledTimes(1)
    expect(store.state.strategyManagement).toEqual({
      strategies: [{ id: 's1' }],
      templates: [{ id: 't1' }]
    })
    expect(store.state.error).toBeNull()
    expect(store.state.lastFetch).not.toBeNull()
  })

  it('surfaces strategy-management fetch failures through standardized state', async () => {
    mockTradingApiManager.getStrategyManagement.mockRejectedValue(new Error('strategy unavailable'))

    const store = useStrategyStore()

    await expect(store.loadStrategyManagement()).rejects.toThrow('strategy unavailable')
    expect(store.state.error).toBe('strategy unavailable')
    expect(store.state.strategyManagement).toEqual({
      strategies: [],
      templates: []
    })
  })
})
