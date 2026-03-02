import { describe, expect, it, beforeEach } from 'vitest'
import {
  useStrategyCrossTabContext,
  __resetStrategyCrossTabContextForTests
} from '@/composables/strategy/useStrategyCrossTabContext'

describe('useStrategyCrossTabContext', () => {
  beforeEach(() => {
    __resetStrategyCrossTabContextForTests()
  })

  it('upserts list snapshots and preserves existing parameter snapshots on list refresh', () => {
    const context = useStrategyCrossTabContext()

    context.upsertFromStrategyList([
      {
        id: 's1',
        code: 'momentum',
        name: 'Momentum A',
        type: 'momentum',
        status: 'running',
        lastRunTime: '2026-03-01T10:00:00Z',
        nextRunTime: '-',
        totalReturn: '-',
        sharpeRatio: '-',
        maxDrawdown: '-',
        winRate: '-',
        description: 'demo'
      }
    ])

    context.setParametersSnapshot('s1', { fast: 10, slow: 30 })

    context.upsertFromStrategyList([
      {
        id: 's1',
        code: 'momentum',
        name: 'Momentum A2',
        type: 'momentum',
        status: 'paused',
        lastRunTime: '2026-03-01T11:00:00Z',
        nextRunTime: '-',
        totalReturn: '-',
        sharpeRatio: '-',
        maxDrawdown: '-',
        winRate: '-',
        description: 'demo-2'
      }
    ])

    const snapshot = context.getSnapshot('s1')
    expect(snapshot).not.toBeNull()
    expect(snapshot?.name).toBe('Momentum A2')
    expect(snapshot?.status).toBe('paused')
    expect(snapshot?.parameters).toEqual({ fast: 10, slow: 30 })
  })

  it('updates status/parameters and removes snapshots by strategyId', () => {
    const context = useStrategyCrossTabContext()

    context.upsertFromStrategyList([
      {
        id: 's2',
        code: 'mean',
        name: 'Mean Rev',
        type: 'mean_reversion',
        status: 'stopped',
        lastRunTime: '-',
        nextRunTime: '-',
        totalReturn: '-',
        sharpeRatio: '-',
        maxDrawdown: '-',
        winRate: '-',
        description: ''
      }
    ])

    context.setStatusSnapshot('s2', 'running')
    context.setParametersSnapshot('s2', { window: 20 })
    expect(context.getSnapshot('s2')?.status).toBe('running')
    expect(context.getSnapshot('s2')?.parameters).toEqual({ window: 20 })

    context.removeSnapshot('s2')
    expect(context.getSnapshot('s2')).toBeNull()
  })

  it('tracks backtest task snapshot lifecycle', () => {
    const context = useStrategyCrossTabContext()

    context.upsertFromStrategyList([
      {
        id: 's3',
        code: 'breakout',
        name: 'Breakout 1',
        type: 'breakout',
        status: 'running',
        lastRunTime: '-',
        nextRunTime: '-',
        totalReturn: '-',
        sharpeRatio: '-',
        maxDrawdown: '-',
        winRate: '-',
        description: ''
      }
    ])

    context.setBacktestTaskSnapshot('s3', {
      status: 'running',
      taskId: 'task-1',
      message: 'polling',
      updatedAt: '2026-03-01T00:00:00Z'
    })

    expect(context.getSnapshot('s3')?.backtest).toEqual({
      status: 'running',
      taskId: 'task-1',
      message: 'polling',
      updatedAt: '2026-03-01T00:00:00Z'
    })

    context.clearBacktestTaskSnapshot('s3')
    expect(context.getSnapshot('s3')?.backtest).toBeUndefined()
  })

  it('keeps backtest snapshot when parameters are updated', () => {
    const context = useStrategyCrossTabContext()

    context.upsertFromStrategyList([
      {
        id: 's4',
        code: 'pairs',
        name: 'Pairs 1',
        type: 'pairs_trading',
        status: 'running',
        lastRunTime: '-',
        nextRunTime: '-',
        totalReturn: '-',
        sharpeRatio: '-',
        maxDrawdown: '-',
        winRate: '-',
        description: ''
      }
    ])

    context.setBacktestTaskSnapshot('s4', {
      status: 'queued',
      taskId: 'task-42'
    })
    context.setParametersSnapshot('s4', { lookback: 120 })

    expect(context.getSnapshot('s4')?.parameters).toEqual({ lookback: 120 })
    expect(context.getSnapshot('s4')?.backtest).toEqual({
      status: 'queued',
      taskId: 'task-42'
    })
  })

  it('tracks optimization snapshot and preserves it across status updates', () => {
    const context = useStrategyCrossTabContext()

    context.upsertFromStrategyList([
      {
        id: 's5',
        code: 'momentum',
        name: 'Momentum 5',
        type: 'momentum',
        status: 'running',
        lastRunTime: '-',
        nextRunTime: '-',
        totalReturn: '-',
        sharpeRatio: '-',
        maxDrawdown: '-',
        winRate: '-',
        description: ''
      }
    ])

    context.setOptimizationSnapshot('s5', {
      score: 91,
      recommendedParameters: {
        lookback: 34
      },
      writebackTargets: ['management', 'parameters', 'backtest'],
      updatedAt: '2026-03-01T00:00:00Z'
    })
    context.setStatusSnapshot('s5', 'paused')

    expect(context.getSnapshot('s5')?.status).toBe('paused')
    expect(context.getSnapshot('s5')?.optimization).toEqual({
      score: 91,
      recommendedParameters: {
        lookback: 34
      },
      writebackTargets: ['management', 'parameters', 'backtest'],
      updatedAt: '2026-03-01T00:00:00Z'
    })

    context.clearOptimizationSnapshot('s5')
    expect(context.getSnapshot('s5')?.optimization).toBeUndefined()
  })
})
