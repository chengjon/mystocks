import type { StrategyConfig } from '@/api/types/common'
import { mockStrategyList } from './strategyMock'

export interface StrategySignalItem {
  symbol: string
  name: string
  type: 'BUY' | 'SELL' | 'HOLD'
  price: number
  time: string
  strategy: string
}

interface StrategySignalsPayload {
  items?: Array<Partial<StrategySignalItem> & Record<string, unknown>>
}

function normalizeSignalType(type?: unknown): StrategySignalItem['type'] {
  if (typeof type !== 'string') {
    return 'HOLD'
  }

  const normalized = type.toUpperCase()
  if (normalized === 'BUY' || normalized === 'SELL' || normalized === 'HOLD') {
    return normalized
  }

  return 'HOLD'
}

export function createMockStrategySignals(): StrategySignalItem[] {
  return [
    { symbol: '600519', name: '贵州茅台', type: 'BUY', price: 1720.5, time: '14:25:01', strategy: 'TrendFollow' },
    { symbol: '300750', name: '宁德时代', type: 'SELL', price: 195.2, time: '14:20:15', strategy: 'MeanReversion' },
    { symbol: '000001', name: '平安银行', type: 'BUY', price: 10.45, time: '13:55:42', strategy: 'Alpha_V2' }
  ]
}

export function createStrategySignalsFromResponse(payload: unknown): StrategySignalItem[] {
  const data = (payload ?? {}) as StrategySignalsPayload

  if (!Array.isArray(data.items)) {
    return []
  }

  return data.items.map((item, index) => ({
    symbol: typeof item.symbol === 'string' ? item.symbol : `UNKNOWN-${index + 1}`,
    name: typeof item.name === 'string' ? item.name : '未知标的',
    type: normalizeSignalType(item.type),
    price: typeof item.price === 'number' ? item.price : 0,
    time: typeof item.time === 'string' ? item.time : '--:--:--',
    strategy: typeof item.strategy === 'string' ? item.strategy : 'N/A'
  }))
}

function normalizeStrategyType(type?: unknown): StrategyConfig['strategy_type'] {
  if (type === 'momentum' || type === 'mean_reversion' || type === 'breakout' || type === 'grid' || type === 'custom') {
    return type
  }
  return 'momentum'
}

export function createMockStrategyManagementList(): StrategyConfig[] {
  return mockStrategyList.strategies.map((item, index) => {
    const parameterEntries = Object.entries(item.parameters ?? {})
    return {
      strategy_id: Number(item.id ?? index + 1),
      strategy_name: item.name,
      strategy_type: normalizeStrategyType(item.type),
      description: item.description,
      parameters: parameterEntries.map(([name, value]) => ({
        name,
        value,
        data_type: typeof value
      })),
      status: item.status === 'inactive' ? 'archived' : item.status === 'testing' ? 'paused' : item.status,
      updated_at: item.updated_at instanceof Date ? item.updated_at.toISOString() : item.updated_at
    }
  })
}
