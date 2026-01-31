/**
 * Mock数据文件: Backtest Analysis
 * 提供回测分析的模拟数据
 */

/**
 * @typedef {Object} Trade
 * @property {string} date - 交易日期
 * @property {string} type - 交易类型
 * @property {number} price - 交易价格
 * @property {number} quantity - 交易数量
 * @property {number} pnl - 盈亏
 */

/**
 * @typedef {Object} EquityPoint
 * @property {string} date - 日期
 * @property {number} equity - 权益
 * @property {number} drawdown - 回撤
 */

/**
 * @typedef {Object} BacktestResult
 * @property {number} totalReturn - 总收益率
 * @property {number} annualReturn - 年化收益率
 * @property {number} maxDrawdown - 最大回撤
 * @property {number} sharpeRatio - 夏普比率
 * @property {number} winRate - 胜率
 * @property {number} totalTrades - 总交易次数
 * @property {number} profitFactor - 盈利因子
 * @property {number} calmarRatio - 卡玛比率
 * @property {Trade[]} trades - 交易记录
 * @property {EquityPoint[]} equityCurve - 权益曲线
 */

/**
 * 获取回测结果Mock数据
 * @returns {BacktestResult} 回测结果数据
 */
export function getMockBacktestResult() {
  return {
    totalReturn: 0.234, // 23.4%
    annualReturn: 0.089, // 8.9%
    maxDrawdown: -0.156, // -15.6%
    sharpeRatio: 1.23,
    winRate: 0.587, // 58.7%
    totalTrades: 124,
    profitFactor: 1.45,
    calmarRatio: 0.57,
    trades: [
      { date: '2024-01-15', type: 'BUY', price: 10.50, quantity: 1000, pnl: 250.00 },
      { date: '2024-02-01', type: 'SELL', price: 10.75, quantity: 1000, pnl: -250.00 },
      { date: '2024-02-15', type: 'BUY', price: 10.60, quantity: 1000, pnl: 180.00 },
      { date: '2024-03-01', type: 'SELL', price: 10.78, quantity: 1000, pnl: 180.00 }
    ],
    equityCurve: [
      { date: '2024-01-01', equity: 100000, drawdown: 0 },
      { date: '2024-01-15', equity: 100250, drawdown: 0 },
      { date: '2024-02-01', equity: 100000, drawdown: 0.25 },
      { date: '2024-02-15', equity: 100180, drawdown: 0.07 },
      { date: '2024-03-01', equity: 100360, drawdown: 0 }
    ]
  }
}
