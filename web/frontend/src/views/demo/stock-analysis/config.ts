/**
 * Stock-Analysis Demo 配置文件
 */

export interface TabItem {
  key: string
  label: string
  icon: string
}

export interface FileFormat {
  type: string
  extension: string
  recordSize: string
  description: string
}

export interface DayStructure {
  offset: string
  size: string
  type: string
  field: string
  description: string
}

export interface BacktestMetric {
  metric: string
  description: string
}

// Tab 导航配置
export const TABS: TabItem[] = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'data', label: '数据解析', icon: '📂' },
  { key: 'strategy', label: '筛选策略', icon: '🔍' },
  { key: 'backtest', label: '回测系统', icon: '📈' },
  { key: 'realtime', label: '实时监控', icon: '⏰' },
  { key: 'status', label: '集成状态', icon: '✅' }
]

// 文件格式数据
export const FILE_FORMAT_DATA: FileFormat[] = [
  { type: '日线', extension: '.day', recordSize: '32字节', description: '每条记录包含日期、OHLC、成交量和成交额' },
  { type: '分钟线', extension: '.lc1', recordSize: '32字节', description: '1分钟K线数据' },
  { type: '5分钟线', extension: '.lc5', recordSize: '32字节', description: '5分钟K线数据' },
  { type: '财务数据', extension: '.gbbq', recordSize: '变长', description: '股本变迁、除权除息数据' }
]

// 日线数据结构
export const DAY_STRUCTURE_DATA: DayStructure[] = [
  { offset: '0-3', size: '4', type: 'uint32', field: 'date', description: '日期 (YYYYMMDD 格式)' },
  { offset: '4-7', size: '4', type: 'uint32', field: 'open', description: '开盘价 (需除以100)' },
  { offset: '8-11', size: '4', type: 'uint32', field: 'high', description: '最高价 (需除以100)' },
  { offset: '12-15', size: '4', type: 'uint32', field: 'low', description: '最低价 (需除以100)' },
  { offset: '16-19', size: '4', type: 'uint32', field: 'close', description: '收盘价 (需除以100)' },
  { offset: '20-23', size: '4', type: 'float', field: 'amount', description: '成交额 (元)' },
  { offset: '24-27', size: '4', type: 'uint32', field: 'volume', description: '成交量 (手)' },
  { offset: '28-31', size: '4', type: 'uint32', field: 'reserved', description: '保留字段' }
]

// 回测指标
export const BACKTEST_METRICS: BacktestMetric[] = [
  { metric: 'Total Returns', description: '总收益率' },
  { metric: 'Annual Returns', description: '年化收益率' },
  { metric: 'Max Drawdown', description: '最大回撤' },
  { metric: 'Sharpe Ratio', description: '夏普比率 (风险调整后收益)' },
  { metric: 'Sortino Ratio', description: '索提诺比率 (下行风险调整后收益)' },
  { metric: 'Win Rate', description: '胜率 (盈利交易占比)' },
  { metric: 'Profit Factor', description: '盈亏比 (总盈利/总亏损)' },
  { metric: 'Total Trades', description: '总交易次数' },
  { metric: 'Average Holding Days', description: '平均持仓天数' }
]
