import { describe, expect, it } from 'vitest'
import type { StrategyConfig } from '@/api/types/common'
import type { StrategySnapshot } from '@/composables/strategy/useStrategyCrossTabContext'
import {
  buildOptimizationRows,
  createMockOptimizationRows,
  toOptimizationStatusLabel
} from '@/views/artdeco-pages/strategy-tabs/strategyOptimizationViewModel'

function createStrategyConfig(id: number, overrides: Partial<StrategyConfig> = {}): StrategyConfig {
  return {
    strategy_id: id,
    strategy_name: `策略 ${id}`,
    strategy_type: 'momentum',
    status: 'active',
    parameters: [],
    ...overrides
  }
}

function createSnapshot(id: string, overrides: Partial<StrategySnapshot> = {}): StrategySnapshot {
  return {
    id,
    name: `快照策略 ${id}`,
    type: 'momentum',
    status: 'running',
    lastRunTime: '-',
    parameters: { lookback: 20 },
    ...overrides
  }
}

describe('strategyOptimizationViewModel', () => {
  it('maps strategy status to optimization status labels', () => {
    expect(toOptimizationStatusLabel('active')).toBe('RUNNING')
    expect(toOptimizationStatusLabel('paused')).toBe('PAUSED')
    expect(toOptimizationStatusLabel('draft')).toBe('STOPPED')
    expect(toOptimizationStatusLabel('archived')).toBe('STOPPED')
  })

  it('builds optimization rows and merges cross-tab snapshot fields', () => {
    const strategies: StrategyConfig[] = [
      createStrategyConfig(1, {
        strategy_name: '动量增强',
        status: 'active',
        parameters: [{ name: 'threshold', value: 1.5 }]
      })
    ]
    const snapshots: Record<string, StrategySnapshot> = {
      '1': createSnapshot('1', {
        status: 'paused',
        parameters: { threshold: 2.1, hold_days: 8 },
        backtest: {
          status: 'running',
          taskId: 'task-21'
        }
      })
    }

    const rows = buildOptimizationRows(strategies, snapshots)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({
      strategyId: '1',
      strategyName: '动量增强',
      statusLabel: 'PAUSED',
      parameterCount: 2,
      backtestStatus: 'RUNNING',
      recommendedParameters: {
        threshold: 2.1,
        hold_days: 8
      }
    })
  })

  it('creates deterministic mock rows for fallback mode', () => {
    const rows = createMockOptimizationRows()
    expect(rows.length).toBeGreaterThan(0)
    expect(rows[0]).toMatchObject({
      source: 'mock'
    })
  })
})
