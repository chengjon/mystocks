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

export interface SectorDistributionItem {
  name: string
  percent: number
}

export interface ConcentrationMetric {
  label: string
  current: number
  limit: number
  variant: 'gold' | 'success' | 'warning'
}

export type RiskTabKey = 'overview' | 'stock'

export interface RiskTabDefinition {
  key: RiskTabKey
  label: string
  icon: string
  eyebrow: string
  description: string
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

export const riskPageConfig = {
  title: '风险管理中心',
  subtitle: '实时监控投资组合风险，设置止损策略，接收风险预警通知',
  showStatus: true,
  statusText: '监控中',
  statusType: 'success' as const,
  showRefresh: true,
  showStats: true,
  showTabs: true,
  apiUrl: '',
  skeleton: { columns: 4, rows: 3 },
  emptyMessage: '暂无风险数据',
  permission: '',
  cacheTime: 300000
}

export const riskTabs: RiskTabDefinition[] = [
  {
    key: 'overview',
    label: '风险概览',
    icon: 'RiskManagement',
    eyebrow: 'portfolio shield',
    description: '聚合组合预警、仓位集中度与行业暴露，作为风险控制的主监控台。'
  },
  {
    key: 'stock',
    label: '个股分析',
    icon: 'StockAnalysis',
    eyebrow: 'single-name lens',
    description: '下钻单一标的的仓位、止损与波动特征，形成可执行的个股风控动作。'
  }
]

export function getRiskTabMeta(tabKey: string | undefined): RiskTabDefinition {
  return riskTabs.find((tab) => tab.key === tabKey) ?? riskTabs[0]
}

export const sectorDistribution: SectorDistributionItem[] = [
  { name: '科技股', percent: 35 },
  { name: '医药生物', percent: 25 },
  { name: '新能源', percent: 20 },
  { name: '金融', percent: 12 },
  { name: '其他', percent: 8 }
]

export const sectorColors = [
  'linear-gradient(90deg, var(--artdeco-bronze), var(--artdeco-gold-primary))',
  'linear-gradient(90deg, var(--artdeco-info), var(--artdeco-gold-light))',
  'linear-gradient(90deg, var(--artdeco-down), var(--artdeco-info))',
  'linear-gradient(90deg, var(--artdeco-fg-muted), var(--artdeco-fg-primary))',
  'linear-gradient(90deg, var(--artdeco-bg-elevated), var(--artdeco-fg-muted))'
]

export const concentrationMetrics: ConcentrationMetric[] = [
  { label: '前10大重仓股占比', current: 65, limit: 70, variant: 'gold' },
  { label: '单股最大仓位', current: 12, limit: 15, variant: 'success' },
  { label: '行业集中度 HHI', current: 0.18, limit: 0.25, variant: 'success' },
  { label: '总仓位', current: 92, limit: 95, variant: 'warning' }
]

export function createInitialRiskMetrics(): RiskMetrics {
  return {
    totalAssets: 1250000,
    totalAssetsChange: 2.5,
    todayProfit: 31250,
    todayProfitChange: 2.57,
    maxDrawdown: 8.5,
    sharpeRatio: 1.35,
    volatility: 18.2,
    beta: 1.12,
    sortinoRatio: 2.1,
    positionValue: 1150000
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
      code: '000858.SZ',
      name: '五粮液',
      riskLevel: 'medium',
      position: 8.3,
      stopStatus: 'normal',
      action: '监控'
    },
    {
      code: '002594.SZ',
      name: '比亚迪',
      riskLevel: 'high',
      position: 15.2,
      stopStatus: 'triggered',
      action: '止损'
    },
    {
      code: '600519.SH',
      name: '贵州茅台',
      riskLevel: 'low',
      position: 20.1,
      stopStatus: 'normal',
      action: '持有'
    }
  ]
}

export function formatRiskCurrencyNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

export function mergeRiskMetrics(current: RiskMetrics, data: unknown): RiskMetrics {
  if (!isRecord(data)) {
    return current
  }

  return { ...current, ...(data as Partial<RiskMetrics>) }
}

export function getRiskLevelLabel(level: RiskAlertItem['riskLevel']): string {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  return '低风险'
}

export function getStopStatusLabel(status: RiskAlertItem['stopStatus']): string {
  if (status === 'triggered') return '已触发'
  if (status === 'approaching') return '接近'
  return '正常'
}
