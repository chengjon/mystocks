import { describe, expect, it } from 'vitest'
import {
  extractStrategyConfigs,
  normalizeProcessTimeMs,
  createStrategyParametersMockFallback
} from '@/views/artdeco-pages/strategy-tabs/strategyParametersData'

describe('strategyParametersData', () => {
  it('normalizes process time to milliseconds', () => {
    expect(normalizeProcessTimeMs('0.5s')).toBe('500.00')
    expect(normalizeProcessTimeMs('125ms')).toBe('125.00')
    expect(normalizeProcessTimeMs('')).toBe('N/A')
    expect(normalizeProcessTimeMs('abc')).toBe('N/A')
  })

  it('extracts strategy configs from common payload containers', () => {
    expect(extractStrategyConfigs([])).toEqual([])
    expect(extractStrategyConfigs({ strategies: [{ strategy_id: 1 }] })).toEqual([{ strategy_id: 1 }])
    expect(extractStrategyConfigs({ items: [{ strategy_id: 2 }] })).toEqual([{ strategy_id: 2 }])
    expect(extractStrategyConfigs({ data: [{ strategy_id: 3 }] })).toEqual([{ strategy_id: 3 }])
    expect(extractStrategyConfigs({})).toBeNull()
  })

  it('provides non-empty mock fallback payload', () => {
    const mockList = createStrategyParametersMockFallback()
    expect(mockList.length).toBeGreaterThan(0)
  })
})
