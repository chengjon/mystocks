export interface KLineRow {
  datetime: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export function buildMarketKlineParams(stockCode: string): Record<string, unknown> {
  return {
    stock_code: stockCode,
    period: "daily",
    limit: 100,
  }
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
