type ApiEnvelope<T> = {
  data?: T
  request_id?: string
}

export type TradeRouteEnvelope<T> = {
  request_id?: string
  status?: string
  endpoint?: string
  resource?: string
} & T

export type ExecuteTradePayload = {
  request_id?: string
  data?: {
    order?: {
      symbol?: string
      direction?: string
      order_type?: string
      quantity?: number
      price?: number
    }
    result?: {
      action?: string
    }
  }
}

export type StatisticsPayload = {
  statistics?: {
    total_trades?: number
    buy_count?: number
    sell_count?: number
    position_count?: number
    total_buy_amount?: number
    total_sell_amount?: number
    total_commission?: number
    realized_profit?: number
  }
}

export const unwrapResponseData = <T>(raw: unknown): T => {
  if (raw && typeof raw === 'object' && 'data' in (raw as Record<string, unknown>)) {
    const outer = raw as ApiEnvelope<T>
    if (outer.data !== undefined) {
      return outer.data
    }
  }

  return raw as T
}

export const asRecord = (value: unknown): Record<string, unknown> =>
  typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}

export const asArray = <T = unknown>(value: unknown): T[] => Array.isArray(value) ? (value as T[]) : []

export const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value)
    ? value
    : typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))
      ? Number(value)
      : fallback

export const asString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : value == null ? fallback : String(value)

export const normalizeAccountPayload = (raw: unknown): Record<string, unknown> => {
  const payload = unwrapResponseData<TradeRouteEnvelope<{ account?: Record<string, unknown> }>>(raw)
  const account = asRecord(payload?.account)

  return {
    totalAssets: asNumber(account.total_assets),
    availableCash: asNumber(account.cash),
    totalMarketValue: asNumber(account.market_value),
    totalPositionValue: asNumber(account.market_value),
    totalPnL: asNumber(account.total_profit_loss),
    totalPnLPercent: `${asNumber(account.profit_loss_percent).toFixed(2)}%`,
    currency: 'CNY',
    assetAllocation: [],
  }
}

export const normalizePositionPayload = (raw: unknown): Record<string, unknown>[] => {
  const payload = unwrapResponseData<TradeRouteEnvelope<{ positions?: unknown[] }>>(raw)
  return asArray(payload?.positions).map((item) => {
    const record = asRecord(item)
    return {
      symbol: asString(record.symbol),
      name: asString(record.symbol_name || record.name || record.symbol),
      quantity: asNumber(record.quantity),
      avgPrice: asNumber(record.cost_price),
      currentPrice: asNumber(record.current_price),
      marketValue: asNumber(record.market_value),
      realizedPnL: 0,
      costBasis: asNumber(record.cost_price) * asNumber(record.quantity),
      lastUpdate: asString(record.last_update),
      side: 'long',
    }
  })
}

export const normalizeTradeRows = (raw: unknown): Record<string, unknown>[] => {
  const payload = unwrapResponseData<TradeRouteEnvelope<{ trades?: unknown[] }>>(raw)
  return asArray(payload?.trades).map((item) => {
    const record = asRecord(item)
    return {
      trade_id: asString(record.trade_id),
      order_id: asString(record.order_id || record.trade_id),
      symbol: asString(record.symbol),
      name: asString(record.symbol),
      action: asString(record.direction || record.side, 'buy'),
      price: asNumber(record.price),
      quantity: asNumber(record.quantity),
      amount: asNumber(record.amount),
      commission: asNumber(record.commission),
      trade_time: asString(record.trade_time),
      trade_type: asString(record.trade_type, 'runtime'),
    }
  })
}

export const normalizeOrderRows = (raw: unknown): Record<string, unknown>[] =>
  normalizeTradeRows(raw).map((record) => ({
    order_id: record.order_id,
    symbol: record.symbol,
    name: record.name,
    side: record.action,
    order_type: 'market',
    quantity: record.quantity,
    price: record.price,
    amount: record.amount,
    status: 'filled',
    filled_quantity: record.quantity,
    filled_amount: record.amount,
    average_price: record.price,
    order_time: record.trade_time,
    update_time: record.trade_time,
    remarks: record.trade_type,
  }))
