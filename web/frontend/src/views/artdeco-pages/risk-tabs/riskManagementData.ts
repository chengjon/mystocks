import type {
  ConcentrationMetric,
  RiskAlertItem,
  RiskMetrics,
  SectorDistributionItem,
} from './riskManagementHelpers'

interface PositionItem {
  symbol?: unknown
  symbol_name?: unknown
  market_value?: unknown
  profit_loss_percent?: unknown
  sector?: unknown
  sector_name?: unknown
  industry?: unknown
  industry_name?: unknown
  stop_status?: unknown
  stopStatus?: unknown
  risk_action?: unknown
  action?: unknown
  policy_ready?: unknown
  policyReady?: unknown
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

function parseOptionalString(value: unknown): string | null {
  return typeof value === 'string' && value.trim().length > 0 ? value.trim() : null
}

function parseOptionalBoolean(value: unknown): boolean | null {
  if (typeof value === 'boolean') {
    return value
  }

  if (typeof value === 'number') {
    if (value === 1) return true
    if (value === 0) return false
  }

  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    if (normalized === 'true' || normalized === '1') return true
    if (normalized === 'false' || normalized === '0') return false
  }

  return null
}

function parseStopStatus(value: unknown): RiskAlertItem['stopStatus'] | null {
  if (value === 'triggered' || value === 'approaching' || value === 'normal' || value === 'unverified') {
    return value
  }

  return null
}

function roundToTwo(value: number): number {
  return Number(value.toFixed(2))
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
      totalAssetsChange: null,
      todayProfit: 0,
      todayProfitChange: null,
      maxDrawdown: null,
      sharpeRatio: null,
      volatility: null,
      beta: null,
      sortinoRatio: null,
      positionValue: 0,
    }
  }

  const totalAssets = parseNumber(payload.total_market_value)
  const todayProfit = parseNumber(payload.total_profit_loss)

  return {
    totalAssets,
    totalAssetsChange: null,
    todayProfit,
    todayProfitChange: null,
    maxDrawdown: null,
    sharpeRatio: null,
    volatility: null,
    beta: null,
    sortinoRatio: null,
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
    const riskLevel: RiskAlertItem['riskLevel'] = position >= 50 ? 'high' : position >= 10 ? 'medium' : 'low'
    const explicitPolicyReady = parseOptionalBoolean(item.policy_ready ?? item.policyReady)
    const explicitStopStatus = parseStopStatus(item.stop_status ?? item.stopStatus)
    const explicitAction = parseOptionalString(item.risk_action ?? item.action)
    const policyReady = explicitPolicyReady ?? (explicitStopStatus !== null || explicitAction !== null)
    const stopStatus: RiskAlertItem['stopStatus'] = policyReady ? explicitStopStatus ?? 'unverified' : 'unverified'
    const action = policyReady ? explicitAction ?? '待复核' : '待复核'

    return {
      code,
      name,
      riskLevel,
      position,
      stopStatus,
      action,
      policyReady,
    }
  })
}

export function toRiskManagementSectorDistribution(raw: unknown): SectorDistributionItem[] {
  const payload = extractPositionsPayload(raw)
  if (!payload || !Array.isArray(payload.positions) || payload.positions.length === 0) {
    return []
  }

  const totals = new Map<string, number>()
  let totalMarketValue = 0

  payload.positions.forEach((item) => {
    const marketValue = parseNumber(item.market_value)
    const sectorName =
      parseOptionalString(item.sector_name) ??
      parseOptionalString(item.industry_name) ??
      parseOptionalString(item.sector) ??
      parseOptionalString(item.industry)

    if (!sectorName || marketValue <= 0) {
      return
    }

    totalMarketValue += marketValue
    totals.set(sectorName, (totals.get(sectorName) ?? 0) + marketValue)
  })

  if (totalMarketValue <= 0 || totals.size === 0) {
    return []
  }

  return Array.from(totals.entries())
    .map(([name, marketValue]) => ({
      name,
      percent: roundToTwo((marketValue / totalMarketValue) * 100),
    }))
    .sort((left, right) => right.percent - left.percent)
}

export function toRiskManagementConcentrationMetrics(raw: unknown): ConcentrationMetric[] {
  const payload = extractPositionsPayload(raw)
  if (!payload || !Array.isArray(payload.positions) || payload.positions.length === 0) {
    return []
  }

  const marketValues = payload.positions
    .map((item) => parseNumber(item.market_value))
    .filter((value) => value > 0)
    .sort((left, right) => right - left)

  const totalMarketValue = marketValues.reduce((sum, value) => sum + value, 0)
  if (totalMarketValue <= 0) {
    return []
  }

  const topTenValue = marketValues.slice(0, 10).reduce((sum, value) => sum + value, 0)
  const largestPosition = marketValues[0] ?? 0

  return [
    {
      label: '前10大重仓股占比',
      current: roundToTwo((topTenValue / totalMarketValue) * 100),
      limit: null,
      variant: 'gold',
    },
    {
      label: '单股最大仓位',
      current: roundToTwo((largestPosition / totalMarketValue) * 100),
      limit: null,
      variant: largestPosition / totalMarketValue >= 0.5 ? 'warning' : 'success',
    },
  ]
}
