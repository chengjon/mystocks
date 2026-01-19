
// @ts-nocheck
/**
 * Strategy Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  StrategyListResponse
} from '@/api/types/generated-types'
import type { Strategy } from '@/api/types/strategy'

// Temporary: Use any for missing generated types
// TODO: Fix type generation to include these types
type StrategyConfigResponse = any
type BacktestResultResponse = any
type TechnicalIndicatorResponse = any

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
  value: any
  defaultValue: any
  options?: ParameterOptionVM[]
  min?: number
  max?: number
  step?: number
  unit?: string
  description: string
}

export interface ParameterOptionVM {
  label: string
  value: any
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
  defaultValue: any
  description: string
  range?: [number, number]
}

export class StrategyAdapter {
  /**
   * Convert strategy list response to ViewModel
   */
  static toStrategyListVM(data: StrategyListResponse[]): StrategyListItemVM[] {
    return data.map((item: any) => ({
      id: item.id || '',
      code: item.strategyCode || item.code || '',
      name: item.name || item.displayName || '',
      type: item.type || 'custom',
      status: this.getStrategyStatus(item.status),
      lastRunTime: item.lastRunTime ? this.formatDateTime(item.lastRunTime) : '从未运行',
      nextRunTime: item.nextRunTime ? this.formatDateTime(item.nextRunTime) : '未设置',
      totalReturn: this.formatPercent(item.totalReturn || 0),
      sharpeRatio: (item.sharpeRatio || 0).toFixed(2),
      maxDrawdown: this.formatPercent(item.maxDrawdown || 0),
      winRate: this.formatPercent(item.winRate || 0),
      description: item.description || ''
    }))
  }

  /**
   * Convert strategy config response to ViewModel
   */
  static toStrategyConfigVM(data: StrategyConfigResponse): StrategyConfigVM {
    return {
      id: data.id || '',
      name: data.name || '',
      description: data.description || '',
      parameters: (data.parameters || []).map(this.toParameterVM),
      canEdit: data.canEdit !== false,
      lastModified: this.formatDateTime(data.lastModified)
    }
  }

  /**
   * Convert backtest result to ViewModel
   */
  static toBacktestResultVM(data: BacktestResultResponse): BacktestResultVM {
    const returns = this.calculateReturns(data.initialCapital, data.finalCapital)

    return {
      strategyId: data.strategyId || '',
      strategyName: data.strategyName || '',
      startDate: data.startDate || '',
      endDate: data.endDate || '',
      initialCapital: data.initialCapital || 0,
      finalCapital: data.finalCapital || 0,
      totalReturn: this.formatPercent(returns),
      annualizedReturn: this.formatPercent(data.annualizedReturn || 0),
      sharpeRatio: (data.sharpeRatio || 0).toFixed(2),
      maxDrawdown: this.formatPercent(data.maxDrawdown || 0),
      winRate: this.formatPercent(data.winRate || 0),
      profitFactor: (data.profitFactor || 0).toFixed(2),
      totalTrades: data.totalTrades || 0,
      equityCurve: (data.equityCurve || []).map(point => ({
        date: point.date,
        equity: point.equity,
        drawdown: point.drawdown || 0
      })),
      metrics: {
        profitAndLoss: data.profitAndLoss || 0,
        grossProfit: data.grossProfit || 0,
        grossLoss: data.grossLoss || 0,
        averageTrade: data.averageTrade || 0,
        averageWin: data.averageWin || 0,
        averageLoss: data.averageLoss || 0,
        largestWin: data.largestWin || 0,
        largestLoss: data.largestLoss || 0,
        consecutiveWins: data.consecutiveWins || 0,
        consecutiveLosses: data.consecutiveLosses || 0
      }
    }
  }

  /**
   * Convert technical indicator to ViewModel
   */
  static toTechnicalIndicatorVM(data: TechnicalIndicatorResponse): TechnicalIndicatorVM {
    return {
      name: data.name || '',
      displayName: data.displayName || data.name || '',
      category: data.category || 'technical',
      parameters: (data.parameters || []).map(param => ({
        name: param.name || '',
        type: param.type || 'number',
        defaultValue: param.defaultValue,
        description: param.description || ''
      })),
      outputs: data.outputs || [],
      description: data.description || '',
      formula: data.formula
    }
  }

  /**
   * Convert parameter to ViewModel
   */
  private static toParameterVM(param: any): StrategyParameterVM {
    return {
      name: param.name || '',
      displayName: param.displayName || param.name || '',
      type: param.type || 'string',
      value: param.value,
      defaultValue: param.defaultValue,
      options: param.options?.map((opt: any) => ({
        label: opt.label || String(opt.value),
        value: opt.value
      })),
      min: param.min,
      max: param.max,
      step: param.step,
      unit: param.unit,
      description: param.description || ''
    }
  }

  /**
   * Get strategy status
   */
  private static getStrategyStatus(status: string | boolean): 'running' | 'stopped' | 'paused' | 'error' {
    if (typeof status === 'boolean') {
      return status ? 'running' : 'stopped'
    }
    switch (status?.toLowerCase()) {
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
  private static formatDateTime(timestamp: string | number | Date): string {
    const date = new Date(timestamp)
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
  static adaptStrategyList(data: any): StrategyListItemVM[] {
    return this.toStrategyListVM(data)
  }

  /**
   * Alias for toStrategyConfigVM
   */
  static adaptStrategyDetail(data: any): StrategyConfigVM {
    return this.toStrategyConfigVM(data)
  }

  /**
   * Alias for toStrategyConfigVM
   */
  static adaptStrategy(data: any): Strategy {
    return {
      id: data.id || data.strategy_id || '',
      strategy_id: data.strategy_id || data.id || '',
      name: data.name || data.strategy_name || '',
      description: data.description || '',
      type: data.type || 'custom',
      status: data.status ? this.getStrategyStatus(data.status) : 'inactive',
      performance: data.performance ? {
        totalReturn: data.performance.total_return || data.performance.totalReturn || 0,
        sharpeRatio: data.performance.sharpe_ratio || data.performance.sharpeRatio || 0,
        maxDrawdown: data.performance.max_drawdown || data.performance.maxDrawdown || 0,
        winRate: data.performance.win_rate || data.performance.winRate || 0,
      } : null,
      createdAt: data.created_at ? new Date(data.created_at) : new Date(),
      updatedAt: data.updated_at ? new Date(data.updated_at) : new Date(),
    }
  }

  /**
   * Alias for toBacktestResultVM
   */
  static adaptBacktestTask(data: any): BacktestResultVM | null {
    if (!data) return null
    return this.toBacktestResultVM(data)
  }
}

export default StrategyAdapter
