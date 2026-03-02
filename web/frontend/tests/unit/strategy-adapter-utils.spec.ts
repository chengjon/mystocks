import { describe, expect, it } from 'vitest'
import { StrategyAdapter } from '@/utils/strategy-adapters'

describe('StrategyAdapter utils', () => {
  it('maps strategy status variants into canonical VM statuses', () => {
    const rows = StrategyAdapter.toStrategyListVM([
      {
        id: 's1',
        strategyCode: 'alpha',
        name: 'Alpha',
        type: 'custom',
        status: 'enabled',
        totalReturn: 0.12,
        sharpeRatio: 1.8,
        maxDrawdown: -0.08,
        winRate: 0.65
      },
      {
        id: 's2',
        strategyCode: 'beta',
        name: 'Beta',
        type: 'custom',
        status: false,
        totalReturn: 0,
        sharpeRatio: 0,
        maxDrawdown: 0,
        winRate: 0
      }
    ] as never[])

    expect(rows[0].status).toBe('running')
    expect(rows[1].status).toBe('stopped')
  })

  it('adapts snake_case strategy payload to frontend strategy model', () => {
    const strategy = StrategyAdapter.adaptStrategy({
      strategy_id: '101',
      strategy_name: 'Snake Case Strategy',
      status: 'paused',
      performance: {
        total_return: 0.22,
        sharpe_ratio: 1.5,
        max_drawdown: -0.1,
        win_rate: 0.6
      }
    })

    expect(strategy).toMatchObject({
      id: '101',
      strategy_id: '101',
      name: 'Snake Case Strategy',
      status: 'paused'
    })
    expect(strategy.performance).toMatchObject({
      totalReturn: 0.22,
      sharpeRatio: 1.5,
      maxDrawdown: -0.1,
      winRate: 0.6
    })
  })
})
