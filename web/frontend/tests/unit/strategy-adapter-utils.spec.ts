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

  it('parses strict numeric strings across strategy view models', () => {
    const [listRow] = StrategyAdapter.toStrategyListVM([
      {
        id: 'numeric-strings',
        strategyCode: 'alpha',
        name: 'Numeric Strings',
        type: 'custom',
        totalReturn: '0.12',
        sharpeRatio: '1.8',
        maxDrawdown: '-0.08',
        winRate: ' 0.65 '
      }
    ] as never[])

    expect(listRow).toMatchObject({
      totalReturn: '12.00%',
      sharpeRatio: '1.80',
      maxDrawdown: '-8.00%',
      winRate: '65.00%'
    })

    const backtest = StrategyAdapter.toBacktestResultVM({
      strategyId: 'numeric-strings',
      strategyName: 'Numeric Strings',
      initialCapital: '100000',
      finalCapital: '1.125e5',
      annualizedReturn: '0.11',
      sharpeRatio: '1.9',
      maxDrawdown: '-0.09',
      winRate: '6.5e-1',
      profitFactor: '1.35',
      totalTrades: '42',
      equityCurve: [
        {
          date: '2026-06-09',
          equity: '112500',
          drawdown: '-8e-2'
        }
      ],
      profitAndLoss: '12500',
      averageTrade: '2.5E+1'
    })

    expect(backtest).toMatchObject({
      initialCapital: 100000,
      finalCapital: 112500,
      totalReturn: '12.50%',
      annualizedReturn: '11.00%',
      sharpeRatio: '1.90',
      maxDrawdown: '-9.00%',
      winRate: '65.00%',
      profitFactor: '1.35',
      totalTrades: 42,
      equityCurve: [
        {
          equity: 112500,
          drawdown: -0.08
        }
      ],
      metrics: {
        profitAndLoss: 12500,
        averageTrade: 25
      }
    })

    const strategy = StrategyAdapter.adaptStrategy({
      id: 'numeric-strings',
      name: 'Numeric Strings',
      performance: {
        total_return: '0.22',
        sharpe_ratio: '1.5',
        max_drawdown: '-0.1',
        win_rate: '6e-1'
      }
    })

    expect(strategy.performance).toMatchObject({
      totalReturn: 0.22,
      sharpeRatio: 1.5,
      maxDrawdown: -0.1,
      winRate: 0.6
    })
  })

  it('rejects loose or unsafe numeric strings in strategy metrics', () => {
    const [listRow] = StrategyAdapter.toStrategyListVM([
      {
        id: 'unsafe-strings',
        strategyCode: 'alpha',
        name: 'Unsafe Strings',
        type: 'custom',
        totalReturn: '',
        sharpeRatio: '12%',
        maxDrawdown: '1,234',
        winRate: { value: 0.65 }
      }
    ] as never[])

    expect(listRow).toMatchObject({
      totalReturn: '0.00%',
      sharpeRatio: '0.00',
      maxDrawdown: '0.00%',
      winRate: '0.00%'
    })

    const backtest = StrategyAdapter.toBacktestResultVM({
      initialCapital: '0x10',
      finalCapital: 'Infinity',
      annualizedReturn: 'NaN',
      profitFactor: {},
      totalTrades: ''
    })

    expect(backtest).toMatchObject({
      initialCapital: 0,
      finalCapital: 0,
      totalReturn: '0.00%',
      annualizedReturn: '0.00%',
      profitFactor: '0.00',
      totalTrades: 0
    })

    const strategy = StrategyAdapter.adaptStrategy({
      id: 'unsafe-strings',
      name: 'Unsafe Strings',
      performance: {
        total_return: '0x10',
        sharpe_ratio: 'Infinity',
        max_drawdown: 'NaN',
        win_rate: { value: 0.6 }
      }
    })

    expect(strategy.performance).toMatchObject({
      totalReturn: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      winRate: 0
    })
  })

  it('keeps empty strategy payloads inside default view-model boundaries', () => {
    expect(StrategyAdapter.toStrategyListVM(null)).toEqual([])

    expect(StrategyAdapter.toStrategyConfigVM(null)).toMatchObject({
      id: '',
      name: '',
      description: '',
      parameters: [],
      canEdit: true,
      lastModified: ''
    })

    expect(StrategyAdapter.toBacktestResultVM(null)).toMatchObject({
      strategyId: '',
      strategyName: '',
      initialCapital: 0,
      finalCapital: 0,
      totalTrades: 0,
      equityCurve: []
    })

    expect(StrategyAdapter.toTechnicalIndicatorVM(null)).toMatchObject({
      name: '',
      displayName: '',
      category: 'technical',
      parameters: [],
      outputs: []
    })
  })
})
