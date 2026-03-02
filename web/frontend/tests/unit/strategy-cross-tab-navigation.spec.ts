import { describe, expect, it } from 'vitest'
import {
  buildStrategyCrossTabRoute,
  buildQuickBacktestRoute,
  extractQuickRunFlagFromQuery,
  extractStrategyIdFromQuery,
  type StrategyCrossTabTarget
} from '@/views/artdeco-pages/strategy-tabs/strategyCrossTabNavigation'

describe('strategyCrossTabNavigation', () => {
  it('maps each cross-tab target to canonical route name with strategyId query', () => {
    const cases: Array<{ target: StrategyCrossTabTarget; name: string }> = [
      { target: 'parameters', name: 'strategy-parameters' },
      { target: 'signals', name: 'strategy-signals' },
      { target: 'backtest', name: 'strategy-backtest' }
    ]

    for (const item of cases) {
      expect(buildStrategyCrossTabRoute(item.target, '42')).toEqual({
        name: item.name,
        query: { strategyId: '42' }
      })
    }
  })

  it('extracts strategyId from query string/array and rejects missing values', () => {
    expect(extractStrategyIdFromQuery({ strategyId: 'abc' })).toBe('abc')
    expect(extractStrategyIdFromQuery({ strategyId: ['x', 'y'] })).toBe('x')
    expect(extractStrategyIdFromQuery({ strategyId: '' })).toBeNull()
    expect(extractStrategyIdFromQuery({})).toBeNull()
  })

  it('builds quick backtest route with handoff query', () => {
    expect(buildQuickBacktestRoute('s9')).toEqual({
      name: 'strategy-backtest',
      query: {
        strategyId: 's9',
        quickRun: '1'
      }
    })
  })

  it('extracts quickRun flag from query', () => {
    expect(extractQuickRunFlagFromQuery({ quickRun: '1' })).toBe(true)
    expect(extractQuickRunFlagFromQuery({ quickRun: 'true' })).toBe(true)
    expect(extractQuickRunFlagFromQuery({ quickRun: ['1', '0'] })).toBe(true)
    expect(extractQuickRunFlagFromQuery({ quickRun: '0' })).toBe(false)
    expect(extractQuickRunFlagFromQuery({ quickRun: '' })).toBe(false)
    expect(extractQuickRunFlagFromQuery({})).toBe(false)
  })
})
