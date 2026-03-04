export interface StrategySignalItem {
  symbol: string
  name: string
  type: 'BUY' | 'SELL' | 'HOLD'
  price: number
  time: string
  strategy: string
}

type RawSignal = Partial<StrategySignalItem> & Record<string, unknown>

interface SignalPayload {
  items?: RawSignal[]
  data?: RawSignal[]
  records?: RawSignal[]
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

function extractRawItems(payload: unknown): RawSignal[] {
  if (Array.isArray(payload)) {
    return payload as RawSignal[]
  }

  if (!payload || typeof payload !== 'object') {
    return []
  }

  const data = payload as SignalPayload
  if (Array.isArray(data.items)) return data.items
  if (Array.isArray(data.data)) return data.data
  if (Array.isArray(data.records)) return data.records

  return []
}

export function createStrategySignalsFromResponse(payload: unknown): StrategySignalItem[] {
  const items = extractRawItems(payload)
  if (items.length === 0) {
    return []
  }

  return items.map((item, index) => ({
    symbol: typeof item.symbol === 'string' ? item.symbol : `UNKNOWN-${index + 1}`,
    name: typeof item.name === 'string' ? item.name : '未知标的',
    type: normalizeSignalType(item.type),
    price: typeof item.price === 'number' ? item.price : 0,
    time: typeof item.time === 'string' ? item.time : '--:--:--',
    strategy: typeof item.strategy === 'string' ? item.strategy : 'N/A'
  }))
}
