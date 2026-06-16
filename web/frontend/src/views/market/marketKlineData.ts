import type { KLineDataPoint } from '@/utils/indicators'

export interface KLineRow {
  datetime: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

const MARKET_KLINE_PERIOD_ALIASES: Record<string, string> = {
  '1d': 'daily',
  '1w': 'weekly',
  '1m': 'monthly',
}

export function buildMarketKlineParams(
  stockCode: string,
  period: string = "1d",
  refreshSequence?: number
): Record<string, unknown> {
  const backendPeriod = MARKET_KLINE_PERIOD_ALIASES[period] ?? period
  const params: Record<string, unknown> = {
    stock_code: stockCode,
    period: backendPeriod,
    limit: 100,
  }

  if (typeof refreshSequence === 'number' && Number.isFinite(refreshSequence)) {
    params.refresh_seq = refreshSequence
  }

  return params
}

export function extractKlineRows(payload: unknown): KLineRow[] {
  const rows = Array.isArray(payload)
    ? (payload as Array<Record<string, unknown>>)
    : payload &&
        typeof payload === "object" &&
        Array.isArray((payload as { data?: unknown }).data)
      ? (payload as { data: Array<Record<string, unknown>> }).data
      : []

  return rows.map((row, index) => ({
    datetime: String(row.datetime ?? row.time ?? row.date ?? index),
    open: Number(row.open ?? 0),
    high: Number(row.high ?? 0),
    low: Number(row.low ?? 0),
    close: Number(row.close ?? 0),
    volume: Number(row.volume ?? 0),
  }))
}

function parseKlineTimestamp(value: string, index: number): number {
  const parsed = Date.parse(value)
  if (!Number.isNaN(parsed)) {
    return parsed
  }

  const numeric = Number(value)
  if (Number.isFinite(numeric) && numeric > 0) {
    return numeric
  }

  return Date.now() + index
}

export function toMarketKlineDataPoints(rows: KLineRow[]): KLineDataPoint[] {
  return rows.map((row, index) => ({
    timestamp: parseKlineTimestamp(row.datetime, index),
    open: row.open,
    high: row.high,
    low: row.low,
    close: row.close,
    volume: row.volume,
  }))
}
