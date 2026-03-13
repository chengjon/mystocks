export interface RiskMetrics {
  totalAssets: number
  totalAssetsChange: number
  todayProfit: number
  todayProfitChange: number
  maxDrawdown: number
  sharpeRatio: number
  volatility: number
  beta: number
  sortinoRatio: number
  positionValue: number
}

export interface RiskAlertItem {
  code: string
  name: string
  riskLevel: 'high' | 'medium' | 'low'
  position: number
  stopStatus: 'triggered' | 'approaching' | 'normal'
  action: string
}

export const riskPageConfig = {
  title: '风险管理中心',
  subtitle: '实时监控组合风险、仓位集中度与告警状态',
  showStatus: true,
  statusText: '监控中',
  statusType: 'success' as const,
  showRefresh: true,
  showStats: true,
  showTabs: true,
  skeleton: { columns: 4, rows: 3 },
  emptyMessage: '暂无风险数据',
  permission: 'artdeco:risk:view',
  cacheTime: 300000
}

export const riskTabs = [
  { key: 'overview', label: '风险概览', icon: 'grid' },
  { key: 'stock', label: '个股分析', icon: 'chart' }
]

export function createInitialRiskMetrics(): RiskMetrics {
  return {
    totalAssets: 0,
    totalAssetsChange: 0,
    todayProfit: 0,
    todayProfitChange: 0,
    maxDrawdown: 0,
    sharpeRatio: 0,
    volatility: 0,
    beta: 0,
    sortinoRatio: 0,
    positionValue: 0
  }
}

export function createInitialRiskAlerts(): RiskAlertItem[] {
  return [
    {
      code: '000001.SZ',
      name: '平安银行',
      riskLevel: 'high',
      position: 12.5,
      stopStatus: 'approaching',
      action: '减仓'
    },
    {
      code: '600519.SH',
      name: '贵州茅台',
      riskLevel: 'low',
      position: 8.1,
      stopStatus: 'normal',
      action: '持有'
    }
  ]
}

function toNumber(value: unknown, fallback = 0): number {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : fallback
}

export function mergeRiskMetrics(current: RiskMetrics, payload: unknown): RiskMetrics {
  const source = payload && typeof payload === 'object' ? payload as Record<string, unknown> : {}
  return {
    totalAssets: toNumber(source.totalAssets ?? source.total_assets, current.totalAssets),
    totalAssetsChange: toNumber(source.totalAssetsChange ?? source.total_assets_change, current.totalAssetsChange),
    todayProfit: toNumber(source.todayProfit ?? source.today_profit, current.todayProfit),
    todayProfitChange: toNumber(source.todayProfitChange ?? source.today_profit_change, current.todayProfitChange),
    maxDrawdown: toNumber(source.maxDrawdown ?? source.max_drawdown, current.maxDrawdown),
    sharpeRatio: toNumber(source.sharpeRatio ?? source.sharpe_ratio, current.sharpeRatio),
    volatility: toNumber(source.volatility, current.volatility),
    beta: toNumber(source.beta, current.beta),
    sortinoRatio: toNumber(source.sortinoRatio ?? source.sortino_ratio, current.sortinoRatio),
    positionValue: toNumber(source.positionValue ?? source.position_value, current.positionValue)
  }
}
