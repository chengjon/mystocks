import { apiGet } from '../apiClient.ts'
import type { UnifiedResponse } from '../types/common.ts'

export const STRATEGY_POSITION_API_ROOT = '/v1/trade/positions' as const

export interface StrategyPositionRow {
  symbol: string
  name: string
  quantity: number
  cost: number
  price: number
  marketValue: number
  pnl: number
  pnlPercent: number
  positionPercent: number
}

export interface StrategyPositionSummary {
  totalMarketValue: number
  totalProfitLoss: number
  totalProfitLossPercent: number
  positionsCount: number
  maxPositionPercent: number
}

export interface StrategyPositionSnapshot {
  summary: StrategyPositionSummary
  positions: StrategyPositionRow[]
}

function createEmptySnapshot(): StrategyPositionSnapshot {
  return {
    summary: {
      totalMarketValue: 0,
      totalProfitLoss: 0,
      totalProfitLossPercent: 0,
      positionsCount: 0,
      maxPositionPercent: 0
    },
    positions: []
  }
}

function createErrorResponse(
  message: string,
  requestId = '',
  processTime = '',
  errors?: unknown,
  code = 500
): UnifiedResponse<StrategyPositionSnapshot> {
  return {
    success: false,
    code,
    message,
    data: createEmptySnapshot(),
    timestamp: new Date().toISOString(),
    request_id: requestId,
    process_time: processTime,
    errors
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function parseNumber(value: unknown): number {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : 0
  }

  if (typeof value === 'string' && value.trim()) {
    const parsed = Number.parseFloat(value.replace(/,/g, ''))
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function parseString(value: unknown, fallback = ''): string {
  return typeof value === 'string' && value.trim() ? value : fallback
}

function roundTo(value: number, digits = 2): number {
  const factor = 10 ** digits
  return Math.round(value * factor) / factor
}

function getPayload(raw: unknown): Record<string, unknown> | null {
  if (!isRecord(raw)) {
    return null
  }

  if (typeof raw.success === 'boolean') {
    if (raw.success === false) {
      return null
    }

    if (isRecord(raw.data)) {
      return raw.data
    }
  }

  return raw
}

function normalizeRows(payload: Record<string, unknown>): StrategyPositionRow[] {
  const rawPositions = Array.isArray(payload.positions) ? payload.positions : []
  const rawTotalValue = parseNumber(payload.total_value ?? payload.total_market_value)

  const preliminaryRows = rawPositions.map((item, index) => {
    const record = isRecord(item) ? item : {}
    const symbol = parseString(record.symbol, `UNKNOWN-${index + 1}`)
    const marketValue = parseNumber(record.market_value)
    const rawWeight = parseNumber(record.weight)
    const normalizedWeight = rawWeight <= 1 ? rawWeight * 100 : rawWeight

    return {
      symbol,
      name: parseString(record.name ?? record.symbol_name, symbol),
      quantity: parseNumber(record.quantity),
      cost: parseNumber(record.average_cost ?? record.cost_price),
      price: parseNumber(record.current_price),
      marketValue,
      pnl: parseNumber(record.unrealized_pnl ?? record.profit_loss),
      pnlPercent: parseNumber(record.profit_loss_percent),
      positionPercent: roundTo(normalizedWeight)
    }
  })

  const totalValue = rawTotalValue > 0
    ? rawTotalValue
    : preliminaryRows.reduce((sum, item) => sum + item.marketValue, 0)

  return preliminaryRows
    .map((item) => ({
      ...item,
      positionPercent: item.positionPercent > 0
        ? item.positionPercent
        : (totalValue > 0 ? roundTo((item.marketValue / totalValue) * 100) : 0)
    }))
    .sort((left, right) => right.marketValue - left.marketValue)
}

function buildSummary(payload: Record<string, unknown>, rows: StrategyPositionRow[]): StrategyPositionSummary {
  const totalMarketValue = parseNumber(payload.total_value ?? payload.total_market_value)
    || rows.reduce((sum, item) => sum + item.marketValue, 0)
  const totalProfitLoss = rows.reduce((sum, item) => sum + item.pnl, 0)
  const costBasis = totalMarketValue - totalProfitLoss

  return {
    totalMarketValue: roundTo(totalMarketValue),
    totalProfitLoss: roundTo(totalProfitLoss),
    totalProfitLossPercent: costBasis > 0 ? roundTo((totalProfitLoss / costBasis) * 100) : 0,
    positionsCount: parseNumber(payload.total ?? payload.total_count) || rows.length,
    maxPositionPercent: rows.reduce((max, item) => Math.max(max, item.positionPercent), 0)
  }
}

export const strategyPositionService = {
  async getPositionExposure(): Promise<UnifiedResponse<StrategyPositionSnapshot>> {
    const rawResponse = await apiGet<unknown>(STRATEGY_POSITION_API_ROOT)

    if (isRecord(rawResponse) && rawResponse.success === false) {
      return createErrorResponse(
        parseString(rawResponse.message, '仓位数据加载失败'),
        parseString(rawResponse.request_id),
        parseString(rawResponse.process_time),
        rawResponse.errors,
        parseNumber(rawResponse.code) || 500
      )
    }

    const payload = getPayload(rawResponse)
    if (!payload) {
      return createErrorResponse('仓位数据加载失败')
    }

    const positions = normalizeRows(payload)
    const summary = buildSummary(payload, positions)

    return {
      success: true,
      code: 200,
      message: 'ok',
      data: {
        summary,
        positions
      },
      timestamp: isRecord(rawResponse) ? parseString(rawResponse.timestamp, new Date().toISOString()) : new Date().toISOString(),
      request_id: isRecord(rawResponse) ? parseString(rawResponse.request_id) : '',
      process_time: isRecord(rawResponse) ? parseString(rawResponse.process_time) : '',
      errors: null
    }
  }
}

export default strategyPositionService
