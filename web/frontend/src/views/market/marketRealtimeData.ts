interface RealtimeQuoteItem {
  symbol?: unknown
  name?: unknown
  price?: unknown
  current_price?: unknown
  change_percent?: unknown
  amount?: unknown
  volume?: unknown
}

export interface RealtimeMarketIndexRow {
  symbol: string
  name: string
  current_price: number
  change_percent: number
  amount: number
  volume: number
}

export interface RealtimeMarketOverview {
  indices: RealtimeMarketIndexRow[]
  up_count: number
  down_count: number
  flat_count: number
}

function parseNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value
  }

  if (typeof value === "string" && value.trim()) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function extractQuoteItems(payload: unknown): RealtimeQuoteItem[] {
  if (!payload || typeof payload !== "object") {
    return []
  }

  const candidate = payload as {
    quotes?: unknown
  }

  if (Array.isArray(candidate.quotes)) {
    return candidate.quotes as RealtimeQuoteItem[]
  }

  if (
    candidate.quotes &&
    typeof candidate.quotes === "object" &&
    Array.isArray((candidate.quotes as { data?: unknown }).data)
  ) {
    return (candidate.quotes as { data: RealtimeQuoteItem[] }).data
  }

  return []
}

export function extractRealtimeMarketOverview(payload: unknown): RealtimeMarketOverview {
  const quoteItems = extractQuoteItems(payload)
  const indices = quoteItems.map((item, index) => {
    const changePercent = parseNumber(item.change_percent)
    return {
      symbol: typeof item.symbol === "string" ? item.symbol : `UNKNOWN-${index + 1}`,
      name: typeof item.name === "string" && item.name.trim() ? item.name : `股票${index + 1}`,
      current_price: parseNumber(item.current_price ?? item.price),
      change_percent: changePercent,
      amount: parseNumber(item.amount),
      volume: parseNumber(item.volume),
    }
  })

  return {
    indices,
    up_count: indices.filter((item) => item.change_percent > 0).length,
    down_count: indices.filter((item) => item.change_percent < 0).length,
    flat_count: indices.filter((item) => item.change_percent === 0).length,
  }
}
