export interface PositionApiItem {
  symbol?: unknown
  symbol_name?: unknown
  quantity?: unknown
  cost_price?: unknown
  current_price?: unknown
  market_value?: unknown
  profit_loss?: unknown
  profit_loss_percent?: unknown
}

export interface PositionsPayload {
  positions?: PositionApiItem[]
  total_market_value?: unknown
}

export interface TradeApiItem {
  trade_id?: unknown
  symbol?: unknown
  direction?: unknown
  price?: unknown
  quantity?: unknown
  amount?: unknown
  commission?: unknown
  trade_time?: unknown
  status?: unknown
}

export interface TradesPayload {
  trades?: TradeApiItem[]
}

export interface TradingPositionRow {
  symbol: string
  name: string
  shares: number
  avgCost: number
  currentPrice: number
  marketValue: number
  pnl: number
  pnlPercent: number
  positionPercent: number
}

export interface TradingHistoryRow {
  id: string
  time: string
  symbol: string
  symbolName: string
  type: 'buy' | 'sell'
  typeText: string
  price: number
  quantity: number
  amount: number
  fee: number
  status: 'completed' | 'pending' | 'cancelled'
  statusText: string
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function parseString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback
}

function parseNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function roundTo(value: number, digits = 2): number {
  const factor = 10 ** digits
  return Math.round(value * factor) / factor
}

function extractSymbolName(symbol: string): string {
  const [code] = symbol.split('.')
  return code || symbol
}

function formatDateTime(value: unknown): string {
  if (typeof value !== 'string' || value.trim().length === 0) {
    return ''
  }

  if (value.includes('T')) {
    return value.replace('T', ' ').replace('Z', '').slice(0, 19)
  }

  return value
}

export function extractPositionsPayload(raw: unknown): PositionsPayload | null {
  if (!isRecord(raw)) {
    return null
  }

  if (Array.isArray(raw.positions)) {
    return raw as PositionsPayload
  }

  if (isRecord(raw.data) && Array.isArray(raw.data.positions)) {
    return raw.data as PositionsPayload
  }

  return null
}

export function extractTradesPayload(raw: unknown): TradesPayload | null {
  if (!isRecord(raw)) {
    return null
  }

  if (Array.isArray(raw.trades)) {
    return raw as TradesPayload
  }

  if (isRecord(raw.data) && Array.isArray(raw.data.trades)) {
    return raw.data as TradesPayload
  }

  return null
}

export function toTradingPositionRows(payload: PositionsPayload | null): TradingPositionRow[] {
  if (!payload || !Array.isArray(payload.positions)) {
    return []
  }

  const totalMarketValue = parseNumber(payload.total_market_value)
  const fallbackTotal = payload.positions.reduce((sum, row) => sum + parseNumber(row.market_value), 0)
  const denominator = totalMarketValue > 0 ? totalMarketValue : fallbackTotal

  return payload.positions.map((item, index) => {
    const symbol = parseString(item.symbol, `UNKNOWN-${index + 1}`)
    const marketValue = parseNumber(item.market_value)
    const positionPercent = denominator > 0 ? roundTo((marketValue / denominator) * 100) : 0

    return {
      symbol,
      name: parseString(item.symbol_name, extractSymbolName(symbol)),
      shares: parseNumber(item.quantity),
      avgCost: parseNumber(item.cost_price),
      currentPrice: parseNumber(item.current_price),
      marketValue,
      pnl: parseNumber(item.profit_loss),
      pnlPercent: parseNumber(item.profit_loss_percent),
      positionPercent
    }
  })
}

export function toTradingHistoryRows(payload: TradesPayload | null): TradingHistoryRow[] {
  if (!payload || !Array.isArray(payload.trades)) {
    return []
  }

  return payload.trades.map((item, index) => {
    const symbol = parseString(item.symbol, `UNKNOWN-${index + 1}`)
    const direction = String(item.direction || '').toLowerCase() === 'sell' ? 'sell' : 'buy'
    const normalizedStatus = String(item.status || '').toLowerCase()
    const status = normalizedStatus === 'pending' || normalizedStatus === 'cancelled'
      ? (normalizedStatus as 'pending' | 'cancelled')
      : 'completed'

    return {
      id: parseString(item.trade_id, `trade-${index + 1}`),
      time: formatDateTime(item.trade_time),
      symbol,
      symbolName: extractSymbolName(symbol),
      type: direction,
      typeText: direction === 'buy' ? '买入' : '卖出',
      price: parseNumber(item.price),
      quantity: parseNumber(item.quantity),
      amount: parseNumber(item.amount),
      fee: parseNumber(item.commission),
      status,
      statusText: status === 'pending' ? '待成交' : status === 'cancelled' ? '已撤单' : '已成交'
    }
  })
}
