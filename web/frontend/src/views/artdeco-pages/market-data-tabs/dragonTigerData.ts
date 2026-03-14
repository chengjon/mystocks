export type DragonTigerFilter = "buy" | "sell" | "institution"
export type DragonTigerDateKey = "today" | "yesterday" | "dayBefore"

interface DragonTigerApiItem {
  trade_date?: unknown
  symbol?: unknown
  name?: unknown
  reason?: unknown
  buy_amount?: unknown
  sell_amount?: unknown
  net_amount?: unknown
  turnover_rate?: unknown
  institution_buy?: unknown
  institution_sell?: unknown
}

export interface DragonTigerRow {
  rank: number
  tradeDate: string
  stockInfo: string
  reason: string
  buyAmount: string
  sellAmount: string
  netBuy: string
  turnoverRate: string
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

function formatYi(value: number): string {
  const yi = value / 100000000
  const prefix = yi > 0 ? "+" : ""
  return `${prefix}${yi.toFixed(2)}亿`
}

function normalizeDateKey(value: string): DragonTigerDateKey {
  if (value === "yesterday" || value === "dayBefore") {
    return value
  }
  return "today"
}

function normalizeFilter(value: string): DragonTigerFilter {
  if (value === "sell" || value === "institution") {
    return value
  }
  return "buy"
}

function selectTradeDate(rows: DragonTigerApiItem[], key: DragonTigerDateKey): string | null {
  const uniqueDates = [...new Set(rows.map((row) => String(row.trade_date ?? "")).filter(Boolean))].sort().reverse()
  const index = key === "today" ? 0 : key === "yesterday" ? 1 : 2
  return uniqueDates[index] ?? uniqueDates[0] ?? null
}

function matchesFilter(row: DragonTigerApiItem, filter: DragonTigerFilter): boolean {
  const netAmount = parseNumber(row.net_amount)
  const institutionBuy = parseNumber(row.institution_buy)
  const institutionSell = parseNumber(row.institution_sell)
  const reason = typeof row.reason === "string" ? row.reason : ""

  if (filter === "sell") {
    return netAmount < 0
  }

  if (filter === "institution") {
    return institutionBuy > 0 || institutionSell > 0 || reason.includes("机构")
  }

  return netAmount >= 0
}

export function extractDragonTigerRows(
  payload: unknown,
  filterInput: string = "buy",
  dateInput: string = "today",
): DragonTigerRow[] {
  const rows = Array.isArray(payload) ? (payload as DragonTigerApiItem[]) : []
  if (rows.length === 0) {
    return []
  }

  const filter = normalizeFilter(filterInput)
  const dateKey = normalizeDateKey(dateInput)
  const selectedDate = selectTradeDate(rows, dateKey)

  return rows
    .filter((row) => !selectedDate || String(row.trade_date ?? "") === selectedDate)
    .filter((row) => matchesFilter(row, filter))
    .map((row, index) => ({
      rank: index + 1,
      tradeDate: typeof row.trade_date === "string" ? row.trade_date : "-",
      stockInfo: `${typeof row.name === "string" ? row.name : "未知标的"} (${typeof row.symbol === "string" ? row.symbol : "N/A"})`,
      reason: typeof row.reason === "string" && row.reason ? row.reason : "N/A",
      buyAmount: formatYi(parseNumber(row.buy_amount)),
      sellAmount: formatYi(parseNumber(row.sell_amount)),
      netBuy: formatYi(parseNumber(row.net_amount)),
      turnoverRate: `${parseNumber(row.turnover_rate).toFixed(2)}%`,
    }))
}
