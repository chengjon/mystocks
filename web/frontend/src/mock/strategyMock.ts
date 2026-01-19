/**
 * Strategy Mock Data
 *
 * Fallback data for strategy module when API is unavailable.
 */

import type {
  StrategyVM as Strategy,
  StrategyPerformanceVM as StrategyPerformance,
  BacktestRequestVM as BacktestTask,
  BacktestResultVM,
} from '@/api/types/extensions';

/**
 * Mock strategy performance data
 */
export const mockStrategyPerformance: StrategyPerformance = {
  strategy_id: '1',
  total_return: 0.256,      // 25.6%
  annual_return: 0.312,     // 31.2%
  sharpe_ratio: 1.85,
  max_drawdown: -0.124,     // -12.4%
  win_rate: 0.68,           // 68%
  profit_factor: 2.15,
};

/**
 * Mock strategy list
 */
export const mockStrategyList = {
  strategies: [
    {
      id: '1',
      name: '双均线趋势跟踪',
      description: '基于5日和20日移动平均线的趋势跟踪策略，适合趋势明显的行情',
      type: 'trend_following' as const,
      status: 'active' as const,
      createdAt: new Date('2025-01-15T10:30:00'),
      updatedAt: new Date('2025-01-20T14:22:00'),
      parameters: {
        shortPeriod: 5,
        longPeriod: 20,
        stopLoss: 0.05,
        takeProfit: 0.15,
      },
      performance: { ...mockStrategyPerformance },
    },
    {
      id: '2',
      name: '均值回归策略',
      description: '基于布林带的均值回归策略，适用于震荡市场',
      type: 'mean_reversion' as const,
      status: 'active' as const,
      createdAt: new Date('2025-01-10T09:15:00'),
      updatedAt: new Date('2025-01-18T16:45:00'),
      parameters: {
        period: 20,
        stdDev: 2,
        entryThreshold: 0.02,
        exitThreshold: 0.01,
      },
      performance: {
        strategy_id: '2',
        total_return: 0.189,
        annual_return: 0.234,
        sharpe_ratio: 1.62,
        max_drawdown: -0.098,
        win_rate: 0.72,
        profit_factor: 1.95,
      },
    },
    {
      id: '3',
      name: '动量突破策略',
      description: '捕捉价格突破关键阻力位的机会，适合波动性较大的市场',
      type: 'momentum' as const,
      status: 'testing' as const,
      createdAt: new Date('2025-01-05T11:00:00'),
      updatedAt: new Date('2025-01-22T10:30:00'),
      parameters: {
        lookbackPeriod: 20,
        breakoutThreshold: 0.03,
        volumeConfirm: true,
        stopLoss: 0.04,
      },
      performance: undefined, // 测试中，暂无性能数据
    },
    {
      id: '4',
      name: 'RSI反转策略',
      description: '基于RSI指标的超买超卖反转策略',
      type: 'mean_reversion' as const,
      status: 'inactive' as const,
      createdAt: new Date('2024-12-28T15:20:00'),
      updatedAt: new Date('2025-01-10T09:40:00'),
      parameters: {
        rsiPeriod: 14,
        oversoldThreshold: 30,
        overboughtThreshold: 70,
        positionSize: 0.1,
      },
      performance: {
        strategy_id: '4',
        total_return: 0.145,
        annual_return: 0.178,
        sharpe_ratio: 1.35,
        max_drawdown: -0.089,
        win_rate: 0.65,
        profit_factor: 1.78,
      },
    },
  ],
  total: 4,
  page: 1,
  pageSize: 10,
};

/**
 * Mock single strategy detail
 */
export const mockStrategyDetail: Strategy = mockStrategyList.strategies[0];

/**
 * Mock backtest result
 */
export const mockBacktestResult: BacktestResultVM = {
  task_id: 'bt_20250125_001',
  strategy_id: '1',
  status: 'completed',
  performance: {
    total_return: 0.256,
    annualized_return: 0.312,
    max_drawdown: -0.124,
    sharpe_ratio: 1.85,
    win_rate: 0.68,
  },
  trades: generateMockTrades(20).map(t => ({
    symbol: t.symbol,
    entry_date: t.timestamp.toISOString(),
    exit_date: new Date(t.timestamp.getTime() + 86400000).toISOString(),
    entry_price: t.price,
    exit_price: t.price * (1 + (Math.random() - 0.4) * 0.1),
    pnl: (Math.random() - 0.4) * 1000
  })),
  total_return: 0.256,
  equity_curve: generateMockEquityCurve().map(item => ({
    date: item.date,
    equity: item.value,
    drawdown: item.drawdown
  })),
  created_at: new Date('2025-01-24T10:00:00').toISOString(),
  completed_at: new Date('2025-01-24T10:05:30').toISOString(),
};

/**
 * Mock backtest task
 */
export const mockBacktestTask: BacktestTask = {
  id: 'bt_20250125_001',
  strategy_id: '1',
  status: 'completed',
  created_at: new Date('2025-01-24T10:00:00').toISOString(),
  startTime: new Date('2025-01-24T10:00:00').toISOString(),
  progress: 100,
  result: mockBacktestResult,
};

/**
 * Generate mock equity curve
 */
function generateMockEquityCurve(): Array<{ date: string; value: number; drawdown?: number }> {
  const curve: Array<{ date: string; value: number; drawdown?: number }> = [];
  const startDate = new Date('2024-01-01');
  let value = 100000;
  let peak = value;

  for (let i = 0; i < 252; i++) { // 1 year of trading days
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);

    // Random daily return between -2% and +2.5%
    const dailyReturn = (Math.random() - 0.45) * 0.045;
    value = value * (1 + dailyReturn);

    if (value > peak) {
      peak = value;
    }

    const drawdown = (value - peak) / peak;

    curve.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(value * 100) / 100,
      drawdown: Math.round(drawdown * 10000) / 10000,
    });
  }

  return curve;
}

/**
 * Generate mock trades
 */
function generateMockTrades(count: number) {
  const trades: Array<{
    id: string;
    symbol: string;
    type: 'buy' | 'sell';
    quantity: number;
    price: number;
    timestamp: Date;
    profitLoss?: number;
    profitLossPercent?: number;
  }> = [];

  const symbols = ['600519', '000001', '000002', '600036', '601318'];
  const now = new Date();

  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now);
    timestamp.setDate(timestamp.getDate() - Math.floor(Math.random() * 30));
    timestamp.setHours(9, 30 + Math.floor(Math.random() * 120), 0, 0);

    const type = Math.random() > 0.5 ? 'buy' : 'sell';
    const price = 100 + Math.random() * 50;
    const quantity = Math.floor(100 + Math.random() * 900);

    trades.push({
      id: `trade_${i + 1}`,
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      type,
      quantity,
      price: Math.round(price * 100) / 100,
      timestamp,
      ...(type === 'sell' && {
        profitLoss: Math.round((Math.random() - 0.3) * 5000 * 100) / 100,
        profitLossPercent: Math.round((Math.random() - 0.3) * 20 * 100) / 100,
      }),
    });
  }

  return trades.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
}

/**
 * Mock backtest tasks list
 */
export const mockBacktestTasks: BacktestTask[] = [
  {
    ...mockBacktestTask,
  },
  {
    id: 'bt_20250124_003',
    strategy_id: '2',
    status: 'completed',
    created_at: new Date('2025-01-23T14:00:00').toISOString(),
    progress: 100,
    startTime: new Date('2025-01-23T14:00:00').toISOString(),
    result: {
      ...mockBacktestResult,
      total_return: 0.189,
    },
  },
  {
    id: 'bt_20250125_002',
    strategy_id: '3',
    status: 'running',
    created_at: new Date('2025-01-25T09:30:00').toISOString(),
    progress: 65,
    startTime: new Date('2025-01-25T09:30:00').toISOString(),
  },
];

/**
 * Get random strategy from mock list
 */
export function getRandomStrategy(): Strategy {
  const strategies = mockStrategyList.strategies;
  return strategies[Math.floor(Math.random() * strategies.length)];
}

/**
 * Get strategy by ID
 */
export function getMockStrategyById(id: string): Strategy | undefined {
  return mockStrategyList.strategies.find((s) => s.id === id);
}

/**
 * Get backtest task by ID
 */
export function getMockBacktestById(taskId: string): BacktestTask | undefined {
  return mockBacktestTasks.find((t) => t.id === taskId);
}

export default {
  mockStrategyList,
  mockStrategyDetail,
  mockBacktestTask,
  mockBacktestResult,
  mockBacktestTasks,
  getRandomStrategy,
  getMockStrategyById,
  getMockBacktestById,
};
