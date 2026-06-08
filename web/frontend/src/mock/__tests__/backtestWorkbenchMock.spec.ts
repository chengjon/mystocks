import { describe, expect, it } from 'vitest'
import type { StrategyConfig } from '@/api/types/common'
import { createBacktestWorkbenchRealConfig, getBacktestWorkbenchConfig } from '../backtestWorkbenchMock'

describe('backtestWorkbenchMock', () => {
  it('uses REAL empty baseline config in real mode', () => {
    const config = getBacktestWorkbenchConfig('real')

    expect(config.systemStatus).toContain('策略上下文')
    expect(config.summary.totalRuns).toBe(0)
    expect(config.strategyOptions).toHaveLength(0)
    expect(config.backtestTasks).toHaveLength(0)
    expect(config.opsOverview[1]?.meta).toContain('真实回测任务回填')
  })

  it('keeps empty task baseline when REAL strategy list is empty', () => {
    const config = createBacktestWorkbenchRealConfig([])

    expect(config.summary.totalRuns).toBe(0)
    expect(config.backtestTasks).toHaveLength(0)
    expect(config.systemStatus).toContain('暂无策略')
  })

  it('marks strategy-list derived panels clearly in real config', () => {
    const config = createBacktestWorkbenchRealConfig([
      {
        strategy_id: 101,
        strategy_name: 'Alpha Pulse',
        status: 'active',
        parameters: [{ name: 'window', value: 20, data_type: 'number' }]
      }
    ] as StrategyConfig[])

    expect(config.systemStatus).toContain('策略列表接口可用')
    expect(config.opsOverview[1]?.label).toBe('任务视图')
    expect(config.opsOverview[1]?.meta).toContain('派生')
    expect(config.runLogs[0]?.msg).toContain('等待真实回测结果回填')
  })
})
