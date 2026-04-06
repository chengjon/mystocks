/**
 * Strategy Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  StrategyListResponse
} from '@/api/types/generated-types.ts'
import type { Strategy } from '@/api/types/extensions/strategy.ts'

// Temporary: Use any for missing generated types
// TODO: Fix type generation to include these types
type StrategyConfigResponse = Record<string, unknown>
type BacktestResultResponse = Record<string, unknown>
type TechnicalIndicatorResponse = Record<string, unknown>
type AnyRecord = Record<string, unknown>

const asRecord = (value: unknown): AnyRecord =>
  typeof value === 'object' && value !== null ? (value as AnyRecord) : {}

const asArray = <T = unknown>(value: unknown): T[] =>
  Array.isArray(value) ? (value as T[]) : []

const asString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : value == null ? fallback : String(value)

const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback

type AdaptedStrategy = Strategy & {
  strategy_id: string
  createdAt: Date
  updatedAt: Date
  performance?: Strategy['performance'] & {
    totalReturn: number
    sharpeRatio: number
    maxDrawdown: number
    winRate: number
  }
}

// ViewModel interfaces
export interface StrategyListItemVM {
  id: string
  code: string
  name: string
  type: string
  status: 'running' | 'stopped' | 'paused' | 'error'
  lastRunTime: string
  nextRunTime: string
  totalReturn: string
  sharpeRatio: string
  maxDrawdown: string
  winRate: string
  description: string
}

export interface StrategyConfigVM {
  id: string
  name: string
  description: string
  parameters: StrategyParameterVM[]
  canEdit: boolean
  lastModified: string
  [key: string]: unknown
}

export interface StrategyParameterVM {
  name: string
  displayName: string
  type: 'number' | 'string' | 'boolean' | 'select' | 'date'
  value: unknown
  defaultValue: unknown
  options?: ParameterOptionVM[]
  min?: number
  max?: number
  step?: number
  unit?: string
  description: string
}

export interface ParameterOptionVM {
  label: string
  value: unknown
}

export interface BacktestResultVM {
  // Status fields for polling
  status?: 'pending' | 'running' | 'completed' | 'failed'
  error?: string
  // Result fields
  strategyId: string
  strategyName: string
  startDate: string
  endDate: string
  initialCapital: number
  finalCapital: number
  totalReturn: string
  annualizedReturn: string
  sharpeRatio: string
  maxDrawdown: string
  winRate: string
  profitFactor: string
  totalTrades: number
  equityCurve: EquityCurvePoint[]
  metrics: BacktestMetricsVM
}

export interface BacktestMetricsVM {
  profitAndLoss: number
  grossProfit: number
  grossLoss: number
  averageTrade: number
  averageWin: number
  averageLoss: number
  largestWin: number
  largestLoss: number
  consecutiveWins: number
  consecutiveLosses: number
}

export interface EquityCurvePoint {
  date: string
  equity: number
  drawdown: number
}

export interface TechnicalIndicatorVM {
  name: string
  displayName: string
  category: string
  parameters: IndicatorParameterVM[]
  outputs: string[]
  description: string
  formula?: string
}

export interface IndicatorParameterVM {
  name: string
  type: string
  defaultValue: unknown
  description: string
  range?: [number, number]
}

export class StrategyAdapter {
  private static normalizeStrategyRows(input: StrategyListResponse | unknown[] | unknown): AnyRecord[] {
    if (Array.isArray(input)) {
      return input.map((item) => asRecord(item))
    }

    const record = asRecord(input)
    if (Array.isArray(record.strategies)) {
      return record.strategies.map((item) => asRecord(item))
    }
    if (Array.isArray(record.items)) {
      return record.items.map((item) => asRecord(item))
    }

    return []
  }

  /**
   * Convert strategy list response to ViewModel
   */
  static toStrategyListVM(data: StrategyListResponse | unknown[] | unknown): StrategyListItemVM[] {
    return this.normalizeStrategyRows(data).map((item) => ({
      id: asString(item.id),
      code: asString(item.strategyCode || item.code),
      name: asString(item.name || item.displayName),
      type: asString(item.type, 'custom'),
      status: this.getStrategyStatus(item.status),
      lastRunTime: item.lastRunTime ? this.formatDateTime(item.lastRunTime) : '从未运行',
      nextRunTime: item.nextRunTime ? this.formatDateTime(item.nextRunTime) : '未设置',
      totalReturn: this.formatPercent(asNumber(item.totalReturn)),
      sharpeRatio: asNumber(item.sharpeRatio).toFixed(2),
      maxDrawdown: this.formatPercent(asNumber(item.maxDrawdown)),
      winRate: this.formatPercent(asNumber(item.winRate)),
      description: asString(item.description)
    }))
  }

  /**
   * Convert strategy config response to ViewModel
   */
  static toStrategyConfigVM(data: StrategyConfigResponse): StrategyConfigVM {
    const record = asRecord(data)
    return {
      id: asString(record.id),
      name: asString(record.name),
      description: asString(record.description),
      parameters: asArray(record.parameters).map(this.toParameterVM),
      canEdit: record.canEdit !== false,
      lastModified: this.formatDateTime(record.lastModified)
    }
  }

  /**
   * Convert backtest result to ViewModel
   */
  static toBacktestResultVM(data: BacktestResultResponse): BacktestResultVM {
    const record = asRecord(data)
    const initialCapital = asNumber(record.initialCapital)
    const finalCapital = asNumber(record.finalCapital)
    const returns = this.calculateReturns(initialCapital, finalCapital)

    return {
      strategyId: asString(record.strategyId),
      strategyName: asString(record.strategyName),
      startDate: asString(record.startDate),
      endDate: asString(record.endDate),
      initialCapital,
      finalCapital,
      totalReturn: this.formatPercent(returns),
      annualizedReturn: this.formatPercent(asNumber(record.annualizedReturn)),
      sharpeRatio: asNumber(record.sharpeRatio).toFixed(2),
      maxDrawdown: this.formatPercent(asNumber(record.maxDrawdown)),
      winRate: this.formatPercent(asNumber(record.winRate)),
      profitFactor: asNumber(record.profitFactor).toFixed(2),
      totalTrades: asNumber(record.totalTrades),
      equityCurve: asArray(record.equityCurve).map((point) => {
        const pointRecord = asRecord(point)
        return {
          date: asString(pointRecord.date),
          equity: asNumber(pointRecord.equity),
          drawdown: asNumber(pointRecord.drawdown)
        }
      }),
      metrics: {
        profitAndLoss: asNumber(record.profitAndLoss),
        grossProfit: asNumber(record.grossProfit),
        grossLoss: asNumber(record.grossLoss),
        averageTrade: asNumber(record.averageTrade),
        averageWin: asNumber(record.averageWin),
        averageLoss: asNumber(record.averageLoss),
        largestWin: asNumber(record.largestWin),
        largestLoss: asNumber(record.largestLoss),
        consecutiveWins: asNumber(record.consecutiveWins),
        consecutiveLosses: asNumber(record.consecutiveLosses)
      }
    }
  }

  /**
   * Convert technical indicator to ViewModel
   */
  static toTechnicalIndicatorVM(data: TechnicalIndicatorResponse): TechnicalIndicatorVM {
    const record = asRecord(data)
    return {
      name: asString(record.name),
      displayName: asString(record.displayName || record.name),
      category: asString(record.category, 'technical'),
      parameters: asArray(record.parameters).map((param) => {
        const paramRecord = asRecord(param)
        return {
          name: asString(paramRecord.name),
          type: asString(paramRecord.type, 'number'),
          defaultValue: paramRecord.defaultValue,
          description: asString(paramRecord.description)
        }
      }),
      outputs: asArray<string>(record.outputs),
      description: asString(record.description),
      formula: typeof record.formula === 'string' ? record.formula : undefined
    }
  }

  /**
   * Convert parameter to ViewModel
   */
  private static toParameterVM(param: unknown): StrategyParameterVM {
    const record = asRecord(param)

    return {
      name: asString(record.name),
      displayName: asString(record.displayName || record.name),
      type: asString(record.type, 'string') as StrategyParameterVM['type'],
      value: record.value,
      defaultValue: record.defaultValue,
      options: asArray(record.options).map((opt) => {
        const optionRecord = asRecord(opt)
        return {
          label: asString(optionRecord.label || optionRecord.value),
          value: optionRecord.value
        }
      }),
      min: typeof record.min === 'number' ? record.min : undefined,
      max: typeof record.max === 'number' ? record.max : undefined,
      step: typeof record.step === 'number' ? record.step : undefined,
      unit: typeof record.unit === 'string' ? record.unit : undefined,
      description: asString(record.description)
    }
  }

  /**
   * Get strategy status
   */
  private static getStrategyStatus(status: unknown): 'running' | 'stopped' | 'paused' | 'error' {
    if (typeof status === 'boolean') {
      return status ? 'running' : 'stopped'
    }
    switch (asString(status).toLowerCase()) {
      case 'active':
      case 'running':
      case 'enabled':
        return 'running'
      case 'inactive':
      case 'stopped':
      case 'disabled':
        return 'stopped'
      case 'paused':
        return 'paused'
      case 'error':
      case 'failed':
        return 'error'
      default:
        return 'stopped'
    }
  }

  /**
   * Format percentage
   */
  private static formatPercent(value: number): string {
    return `${(value * 100).toFixed(2)}%`
  }

  /**
   * Format date and time
   */
  private static formatDateTime(timestamp: unknown): string {
    if (!timestamp) return ''
    const normalized = timestamp instanceof Date || typeof timestamp === 'string' || typeof timestamp === 'number'
      ? timestamp
      : asString(timestamp)
    const date = new Date(normalized)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Calculate returns
   */
  private static calculateReturns(initial: number, final: number): number {
    if (initial === 0) return 0
    return (final - initial) / initial
  }

  /**
   * Format currency
   */
  static formatCurrency(amount: number, currency: string = '¥'): string {
    return `${currency}${amount.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`
  }

  /**
   * Format large numbers
   */
  static formatLargeNumber(num: number): string {
    if (num >= 100000000) {
      return `${(num / 100000000).toFixed(1)}亿`
    } else if (num >= 10000) {
      return `${(num / 10000).toFixed(1)}万`
    }
    return num.toLocaleString()
  }

  // ========================================
  // Aliases for backward compatibility
  // ========================================

  /**
   * Alias for toStrategyListVM
   */
  static adaptStrategyList(data: unknown): StrategyListItemVM[] {
    return this.toStrategyListVM(data)
  }

  /**
   * Alias for toStrategyConfigVM
   */
  static adaptStrategyDetail(data: unknown): StrategyConfigVM {
    return this.toStrategyConfigVM(asRecord(data))
  }

  /**
   * Alias for toStrategyConfigVM
   */
  static adaptStrategy(data: unknown): AdaptedStrategy {
    const record = asRecord(data)
    const performance = asRecord(record.performance)
    const createdAt = record.created_at ? new Date(asString(record.created_at)) : new Date()
    const updatedAt = record.updated_at ? new Date(asString(record.updated_at)) : new Date()

    return {
      id: asString(record.id || record.strategy_id),
      strategy_id: asString(record.strategy_id || record.id),
      name: asString(record.name || record.strategy_name),
      description: asString(record.description) || undefined,
      type: (asString(record.type, 'custom') as AdaptedStrategy['type']),
      status: record.status ? (this.getStrategyStatus(record.status) as AdaptedStrategy['status']) : 'inactive',
      parameters: asRecord(record.parameters),
      constraints: undefined,
      risk_limits: undefined,
      performance: Object.keys(performance).length > 0 ? {
        total_return: asNumber(performance.total_return || performance.totalReturn),
        annualized_return: 0,
        sharpe_ratio: asNumber(performance.sharpe_ratio || performance.sharpeRatio),
        sortino_ratio: 0,
        max_drawdown: asNumber(performance.max_drawdown || performance.maxDrawdown),
        volatility: 0,
        value_at_risk: 0,
        total_trades: 0,
        win_rate: asNumber(performance.win_rate || performance.winRate),
        profit_factor: 0,
        average_win: 0,
        average_loss: 0,
        calmar_ratio: 0,
        information_ratio: 0,
        totalReturn: asNumber(performance.total_return || performance.totalReturn),
        sharpeRatio: asNumber(performance.sharpe_ratio || performance.sharpeRatio),
        maxDrawdown: asNumber(performance.max_drawdown || performance.maxDrawdown),
        winRate: asNumber(performance.win_rate || performance.winRate),
      } : undefined,
      created_at: createdAt.toISOString(),
      updated_at: updatedAt.toISOString(),
      createdAt,
      updatedAt,
    }
  }

  /**
   * Alias for toBacktestResultVM
   */
  static adaptBacktestTask(data: unknown): BacktestResultVM | null {
    if (!data) return null
    return this.toBacktestResultVM(asRecord(data))
  }
}

export default StrategyAdapter
