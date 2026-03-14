import type { RiskAlertItem, RiskMetrics } from './riskManagementHelpers'

interface PositionItem {
  symbol?: unknown
  symbol_name?: unknown
  market_value?: unknown
  profit_loss_percent?: unknown
}

interface PositionsPayload {
  positions?: PositionItem[]
  total_market_value?: unknown
  total_profit_loss?: unknown
  total_profit_loss_percent?: unknown
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

function extractPositionsPayload(raw: unknown): PositionsPayload | null {
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

export function toRiskManagementMetrics(raw: unknown): RiskMetrics {
  const payload = extractPositionsPayload(raw)
  if (!payload || !Array.isArray(payload.positions)) {
    return {
      totalAssets: 0,
      totalAssetsChange: 0,
      todayProfit: 0,
      todayProfitChange: 0,
      maxDrawdown: 0,
      sharpeRatio: 0,
      volatility: 0,
      beta: 1,
      sortinoRatio: 0,
      positionValue: 0,
    }
  }

  const totalAssets = parseNumber(payload.total_market_value)
  const todayProfit = parseNumber(payload.total_profit_loss)
  const todayProfitChange = parseNumber(payload.total_profit_loss_percent)

  return {
    totalAssets,
    totalAssetsChange: todayProfitChange,
    todayProfit,
    todayProfitChange,
    maxDrawdown: 0,
    sharpeRatio: 0,
    volatility: 0,
    beta: 1,
    sortinoRatio: 0,
    positionValue: totalAssets,
  }
}

export function toRiskManagementAlerts(raw: unknown): RiskAlertItem[] {
  const payload = extractPositionsPayload(raw)
  if (!payload || !Array.isArray(payload.positions)) {
    return []
  }

  const total = Math.max(
    1,
    payload.positions.reduce((sum, item) => sum + parseNumber(item.market_value), 0),
  )

  return payload.positions.map((item, index) => {
    const code = parseString(item.symbol, `UNKNOWN-${index + 1}`)
    const name = parseString(item.symbol_name, code)
    const position = Number(((parseNumber(item.market_value) / total) * 100).toFixed(2))
    const pnlPct = parseNumber(item.profit_loss_percent)
    const riskLevel: RiskAlertItem['riskLevel'] = position >= 50 ? 'high' : position >= 10 ? 'medium' : 'low'
    const stopStatus: RiskAlertItem['stopStatus'] =
      pnlPct < 0 ? 'triggered' : riskLevel === 'high' ? 'approaching' : 'normal'
    const action =
      stopStatus === 'triggered' ? '止损' :
      riskLevel === 'high' ? '减仓' :
      riskLevel === 'medium' ? '监控' : '持有'

    return {
      code,
      name,
      riskLevel,
      position,
      stopStatus,
      action,
    }
  })
}
