interface MonitoringWatchlistItem {
  id?: unknown
  name?: unknown
  stocks_count?: unknown
}

interface MonitoringWatchlistStockItem {
  stock_code?: unknown
  stock_name?: unknown
  entry_price?: unknown
  weight?: unknown
  stop_loss_price?: unknown
}

interface TradePositionItem {
  symbol?: unknown
  symbol_name?: unknown
  quantity?: unknown
  cost_price?: unknown
  current_price?: unknown
  profit_loss?: unknown
  market_value?: unknown
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
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

function parseString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback
}

function parseId(value: unknown, fallback = ''): string {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return String(value)
  }
  return parseString(value, fallback)
}

function assertSuccessfulEnvelope(raw: unknown, fallbackMessage: string): void {
  if (!isRecord(raw) || raw.success !== false) {
    return
  }

  throw new Error(parseString(raw.message, fallbackMessage))
}

function extractList(raw: unknown): Record<string, unknown>[] {
  if (Array.isArray(raw)) {
    return raw.filter(isRecord)
  }

  if (!isRecord(raw)) {
    return []
  }

  if (Array.isArray(raw.data)) {
    return raw.data.filter(isRecord)
  }

  if (isRecord(raw.data) && Array.isArray(raw.data.data)) {
    return raw.data.data.filter(isRecord)
  }

  return []
}

export function extractMonitoringWatchlists(raw: unknown): Array<{ id: string; name: string; stocks: unknown[] }> {
  assertSuccessfulEnvelope(raw, '监控自选列表加载失败')
  return extractList(raw).map((item) => {
    const row = item as MonitoringWatchlistItem
    const stocksCount = Math.max(0, Math.trunc(parseNumber(row.stocks_count)))
    return {
      id: parseId(row.id, ''),
      name: parseString(row.name, '未命名清单'),
      stocks: Array.from({ length: stocksCount }, () => ({})),
    }
  })
}

export function extractMonitoringWatchlistStocks(
  raw: unknown,
): Array<{
  symbol: string
  name: string
  price: number
  change: string
  volume: string
  weight: string
  stock_code: string
  stock_name: string
  entry_price: number
  stop_loss_price?: unknown
}> {
  assertSuccessfulEnvelope(raw, '监控自选股票加载失败')
  return extractList(raw).map((item, index) => {
    const row = item as MonitoringWatchlistStockItem
    const symbol = parseString(row.stock_code, `UNKNOWN-${index + 1}`)
    return {
      symbol,
      name: parseString(row.stock_name, symbol),
      price: parseNumber(row.entry_price),
      change: '--',
      volume: '--',
      weight: `${parseNumber(row.weight) * 100}`.replace(/\.00$/, '') + '%',
      stock_code: symbol,
      stock_name: parseString(row.stock_name, symbol),
      entry_price: parseNumber(row.entry_price),
      stop_loss_price: (item as Record<string, unknown>).stop_loss_price,
    }
  }).map((row) => ({
    ...row,
    weight: row.weight === '0%' ? '0.00%' : row.weight.includes('.') ? row.weight : `${Number.parseFloat(row.weight).toFixed(2)}%`,
  }))
}

function extractTradePositions(raw: unknown): { positions: TradePositionItem[]; total_market_value?: unknown; total_profit_loss?: unknown; total_profit_loss_percent?: unknown } | null {
  if (!isRecord(raw)) {
    return null
  }

  if (isRecord(raw.data) && Array.isArray(raw.data.positions)) {
    return raw.data as { positions: TradePositionItem[]; total_market_value?: unknown; total_profit_loss?: unknown; total_profit_loss_percent?: unknown }
  }

  if (Array.isArray(raw.positions)) {
    return raw as { positions: TradePositionItem[]; total_market_value?: unknown; total_profit_loss?: unknown; total_profit_loss_percent?: unknown }
  }

  return null
}

export function extractPortfolioMonitorRows(
  raw: unknown,
): Array<{ symbol: string; name: string; quantity: number; cost: number; price: number; pnl: number }> {
  const payload = extractTradePositions(raw)
  if (!payload) {
    return []
  }

  return payload.positions.map((item, index) => {
    const symbol = parseString(item.symbol, `UNKNOWN-${index + 1}`)
    return {
      symbol,
      name: parseString(item.symbol_name, symbol),
      quantity: parseNumber(item.quantity),
      cost: parseNumber(item.cost_price),
      price: parseNumber(item.current_price),
      pnl: parseNumber(item.profit_loss),
    }
  })
}

function formatCurrency(value: number): string {
  return `¥${Math.round(value).toLocaleString('zh-CN')}`
}

export function extractPortfolioMonitorStats(raw: unknown): {
  totalAssets: string
  totalAssetsChange: number
  todayPnl: string
  todayPnlChange: number
  positionCount: number
  positionCountLabel: string
  totalMarketValue: string
} {
  const payload = extractTradePositions(raw)
  if (!payload) {
    return {
      totalAssets: '¥0',
      totalAssetsChange: 0,
      todayPnl: '¥0',
      todayPnlChange: 0,
      positionCount: 0,
      positionCountLabel: '0 个',
      totalMarketValue: '¥0',
    }
  }

  const totalAssets = parseNumber(payload.total_market_value)
  const todayPnl = parseNumber(payload.total_profit_loss)
  const todayPnlChange = parseNumber(payload.total_profit_loss_percent)
  const positionCount = payload.positions.length

  return {
    totalAssets: formatCurrency(totalAssets),
    totalAssetsChange: todayPnlChange,
    todayPnl: `${todayPnl >= 0 ? '+' : ''}${formatCurrency(todayPnl).replace('¥', '¥')}`,
    todayPnlChange,
    positionCount,
    positionCountLabel: `${positionCount} 个`,
    totalMarketValue: formatCurrency(totalAssets),
  }
}
