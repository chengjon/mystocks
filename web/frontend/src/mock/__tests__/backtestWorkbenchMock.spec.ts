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
})
