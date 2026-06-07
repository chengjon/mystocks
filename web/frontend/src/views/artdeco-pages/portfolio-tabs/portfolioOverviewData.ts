export interface TradePositionItem {
  symbol?: unknown
  symbol_name?: unknown
  market_value?: unknown
  profit_loss_percent?: unknown
  target_weight?: unknown
  targetWeight?: unknown
}

export interface TradePositionsPayload {
  positions?: TradePositionItem[]
  total_market_value?: unknown
  total_profit_loss?: unknown
  total_profit_loss_percent?: unknown
}

export interface PortfolioPositionRow {
  symbol: string
  name: string
  market_value: number
  pnl_pct: number
  target_weight: number | null
}

export interface PortfolioOverviewData {
  total_assets: number
  today_pnl: number
  today_pnl_pct: number
  rebalance_policy_ready: boolean
  positions: PortfolioPositionRow[]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function parseNumber(value: unknown): number | null {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

function parseString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback
}

export function extractTradePositionsPayload(raw: unknown): TradePositionsPayload | null {
  if (!isRecord(raw)) {
    return null
  }

  if (Array.isArray(raw.positions)) {
    return raw as TradePositionsPayload
  }

  if (isRecord(raw.data) && Array.isArray(raw.data.positions)) {
    return raw.data as TradePositionsPayload
  }

  return null
}

export function toPortfolioOverviewData(payload: TradePositionsPayload | null): PortfolioOverviewData {
  if (!payload || !Array.isArray(payload.positions)) {
    return {
      total_assets: 0,
      today_pnl: 0,
      today_pnl_pct: 0,
      rebalance_policy_ready: false,
      positions: []
    }
  }

  const positions = payload.positions.map((item, index) => {
    const symbol = parseString(item.symbol, `UNKNOWN-${index + 1}`)
    return {
      symbol,
      name: parseString(item.symbol_name, symbol),
      market_value: parseNumber(item.market_value) ?? 0,
      pnl_pct: parseNumber(item.profit_loss_percent) ?? 0,
      target_weight: parseNumber(item.target_weight ?? item.targetWeight),
    }
  })

  const derivedTotalAssets = positions.reduce((sum, item) => sum + item.market_value, 0)
  const rebalancePolicyReady = positions.length > 0 && positions.every((item) => item.target_weight !== null)

  return {
    total_assets: parseNumber(payload.total_market_value) ?? derivedTotalAssets,
    today_pnl: parseNumber(payload.total_profit_loss) ?? 0,
    today_pnl_pct: parseNumber(payload.total_profit_loss_percent) ?? 0,
    rebalance_policy_ready: rebalancePolicyReady,
    positions
  }
}
