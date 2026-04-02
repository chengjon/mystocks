import { describe, expect, it } from 'vitest'
import { createBacktestWorkbenchRealConfig, getBacktestWorkbenchConfig } from '../backtestWorkbenchMock'

describe('backtestWorkbenchMock', () => {
  it('uses REAL empty baseline config in real mode', () => {
    const config = getBacktestWorkbenchConfig('real')

    expect(config.systemStatus).toContain('REAL')
    expect(config.summary.totalRuns).toBe(0)
    expect(config.strategyOptions).toHaveLength(0)
    expect(config.backtestTasks).toHaveLength(0)
  })

  it('keeps empty task baseline when REAL strategy list is empty', () => {
    const config = createBacktestWorkbenchRealConfig([])

    expect(config.summary.totalRuns).toBe(0)
    expect(config.backtestTasks).toHaveLength(0)
    expect(config.systemStatus).toContain('暂无策略')
  })

  it('derives stable updated labels and log timestamps from strategy payload metadata', () => {
    const config = createBacktestWorkbenchRealConfig([
      {
        strategy_id: 101,
        strategy_name: 'Momentum Alpha',
        status: 'active',
        parameters: [],
        updated_at: '2026-03-01T09:00:00Z'
      },
      {
        strategy_id: 102,
        strategy_name: 'Mean Reversion Beta',
        status: 'paused',
        parameters: [],
        updated_at: '2026-03-01T09:05:00Z'
      }
    ])

    expect(config.lastUpdated).toBe('2026-03-01 09:05')
    expect(config.runLogs[0]?.ts).toBe('09:05:00')
  })
})
