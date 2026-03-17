import type {
  CreateStrategyRequestVM as CreateStrategyRequest,
  UpdateStrategyRequestVM as UpdateStrategyRequest,
  StrategyTypeVM
} from '@/api/types/extensions'
import type { StrategyListItemVM } from '@/utils/strategy-adapters'

export type LifecycleAction = 'start' | 'stop' | 'pause' | 'resume'
export type StrategyStatusFilter = 'all' | StrategyListItemVM['status']
export type FormMode = 'create' | 'edit'
export type FailedOperationType = 'lifecycle' | 'create' | 'update' | 'delete'

export interface ParameterFormItem {
  key: string
  value: string
}

export interface StrategyFormState {
  id: string
  name: string
  description: string
  type: StrategyTypeVM
  parameters: ParameterFormItem[]
}

export interface FailedOperation {
  type: FailedOperationType
  message: string
  strategyId?: string
  action?: LifecycleAction
}

export const PAGE_SIZE = 8

export const DEFAULT_RISK_LIMITS: CreateStrategyRequest['risk_limits'] = {
  daily_pnl_limit: 0.05,
  single_stock_loss_limit: 0.03,
  total_drawdown_limit: 0.15,
  max_holding_period_days: 30,
  max_consecutive_losses: 3,
  max_loss_per_trade: 0.02
}

export const DEFAULT_CONSTRAINTS: CreateStrategyRequest['constraints'] = {
  allowed_symbols: [],
  allowed_sectors: [],
  forbidden_symbols: [],
  trading_hours: {
    start: '09:30',
    end: '15:00'
  },
  market_conditions: []
}

export const strategyTypeOptions: Array<{ label: string; value: StrategyTypeVM }> = [
  { label: '趋势跟踪', value: 'trend_following' },
  { label: '均值回归', value: 'mean_reversion' },
  { label: '动量策略', value: 'momentum' },
  { label: '突破策略', value: 'breakout' },
  { label: '套利策略', value: 'arbitrage' },
  { label: '统计套利', value: 'statistical_arbitrage' },
  { label: '配对交易', value: 'pairs_trading' },
  { label: '市场中性', value: 'market_neutral' }
]

export function createDefaultStrategyForm(): StrategyFormState {
  return {
    id: '',
    name: '',
    description: '',
    type: 'trend_following',
    parameters: []
  }
}

export function normalizeStrategyType(type: string): StrategyTypeVM {
  const normalized = type as StrategyTypeVM
  if (strategyTypeOptions.some((item) => item.value === normalized)) {
    return normalized
  }
  return 'trend_following'
}

export function createEditStrategyForm(strategy: StrategyListItemVM): StrategyFormState {
  return {
    id: strategy.id,
    name: strategy.name,
    description: strategy.description || '',
    type: normalizeStrategyType(strategy.type),
    parameters: []
  }
}

export function parseStrategyParameterValue(value: string): unknown {
  const trimmed = value.trim()
  if (trimmed.length === 0) {
    return ''
  }

  if (trimmed === 'true') {
    return true
  }
  if (trimmed === 'false') {
    return false
  }

  const asNumber = Number(trimmed)
  if (!Number.isNaN(asNumber) && trimmed === String(asNumber)) {
    return asNumber
  }

  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
    try {
      return JSON.parse(trimmed)
    } catch {
      return trimmed
    }
  }

  return trimmed
}

export function buildCustomParameters(parameters: ParameterFormItem[]): Record<string, unknown> {
  const custom: Record<string, unknown> = {}
  for (const item of parameters) {
    if (!item.key) {
      continue
    }
    custom[item.key] = parseStrategyParameterValue(item.value)
  }
  return custom
}

export function buildCreateStrategyPayload(formState: StrategyFormState): CreateStrategyRequest {
  return {
    name: formState.name,
    description: formState.description,
    type: formState.type,
    parameters: {
      custom: buildCustomParameters(formState.parameters)
    },
    constraints: DEFAULT_CONSTRAINTS,
    risk_limits: DEFAULT_RISK_LIMITS
  }
}

export function buildUpdateStrategyPayload(formState: StrategyFormState): UpdateStrategyRequest {
  return {
    id: formState.id,
    name: formState.name,
    description: formState.description,
    parameters: {
      custom: buildCustomParameters(formState.parameters)
    }
  }
}

export function filterStrategies(
  strategies: readonly StrategyListItemVM[],
  keyword: string,
  statusFilter: StrategyStatusFilter
): StrategyListItemVM[] {
  const search = keyword.trim().toLowerCase()
  return strategies.filter((strategy) => {
    const matchedStatus = statusFilter === 'all' || strategy.status === statusFilter
    const matchedKeyword =
      search.length === 0 ||
      strategy.name.toLowerCase().includes(search) ||
      strategy.type.toLowerCase().includes(search)
    return matchedStatus && matchedKeyword
  })
}

export function getTotalPages(totalItems: number, pageSize: number = PAGE_SIZE): number {
  return Math.max(1, Math.ceil(totalItems / pageSize))
}

export function paginateStrategies(
  strategies: readonly StrategyListItemVM[],
  currentPage: number,
  pageSize: number = PAGE_SIZE
): StrategyListItemVM[] {
  const offset = (currentPage - 1) * pageSize
  return strategies.slice(offset, offset + pageSize)
}

export function getStrategyManagementEmptyStateText(options?: {
  error?: string | null
  dataSource?: 'real' | 'mock'
}): string {
  if (options?.error) {
    return options.dataSource === 'mock'
      ? 'MOCK 请求失败，请检查 Mock 服务。'
      : 'REAL 请求失败，请稍后重试。'
  }

  if (options?.dataSource === 'mock') {
    return 'MOCK 数据为空，请补充模拟数据。'
  }

  return 'REAL 数据为空，请先创建策略。'
}

export function formatStrategyStatusLabel(status: StrategyListItemVM['status']): string {
  if (status === 'running') return 'RUNNING'
  if (status === 'paused') return 'PAUSED'
  if (status === 'error') return 'ERROR'
  return 'STOPPED'
}

export function formatStrategyUpdatedTime(timestamp: string): string {
  if (!timestamp || timestamp === '-') {
    return '-'
  }

  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function getLifecycleActionLabel(action: LifecycleAction): string {
  if (action === 'start') return '启动'
  if (action === 'stop') return '停止'
  if (action === 'pause') return '暂停'
  return '恢复'
}

export function mapLifecycleActionToStatus(action: LifecycleAction): StrategyListItemVM['status'] {
  if (action === 'start' || action === 'resume') return 'running'
  if (action === 'pause') return 'paused'
  return 'stopped'
}

export function formatBacktestStatusLabel(status: 'queued' | 'running' | 'completed' | 'failed'): string {
  if (status === 'queued') {
    return '回测状态：排队中'
  }
  if (status === 'running') {
    return '回测状态：执行中'
  }
  if (status === 'completed') {
    return '回测状态：已完成'
  }
  return '回测状态：失败'
}
