export interface StockScreenerRow {
  symbol: string
  name: string
  price: number
  changePercent: number
  volume: number
  amount: number
  pe: number
  marketCap: number
}

export interface StockScreenerFilters {
  priceMin?: number
  priceMax?: number
  peMin?: number
  peMax?: number
  volumeMin?: number
  volumeMax?: number
  amountMin?: number
  amountMax?: number
  changeType?: string
  changePercentMin?: number
  changePercentMax?: number
  marketCapRange?: string
}

export function resolveStocksBasicEndpoint(apiBaseUrl: string): string {
  const normalizedBase = apiBaseUrl.trim().replace(/\/+$/, '') || '/api'

  if (normalizedBase === '/api' || normalizedBase.endsWith('/api')) {
    return `${normalizedBase}/v1/data/stocks/basic`
  }

  return `${normalizedBase}/api/v1/data/stocks/basic`
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

function parseOptionalNumber(value: unknown): number | undefined {
  if (value === undefined || value === null || value === '') {
    return undefined
  }
  const parsed = parseNumber(value)
  return Number.isFinite(parsed) ? parsed : undefined
}

function parseString(value: unknown, fallback = ''): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback
}

function extractRows(raw: unknown): Record<string, unknown>[] {
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

export function extractStockScreenerRows(raw: unknown): StockScreenerRow[] {
  return extractRows(raw).map((row, index) => ({
    symbol: parseString(row.symbol, `UNKNOWN-${index + 1}`),
    name: parseString(row.name, `股票${index + 1}`),
    price: parseNumber(row.price),
    changePercent: parseNumber(row.change_pct ?? row.changePercent),
    volume: parseNumber(row.volume),
    amount: parseNumber(row.turnover ?? row.amount),
    pe: parseNumber(row.pe ?? row.pe_ratio),
    marketCap: parseNumber(row.market_cap ?? row.marketCap),
  }))
}

export function filterStockScreenerRows(rows: StockScreenerRow[], filters: StockScreenerFilters): StockScreenerRow[] {
  const priceMin = parseOptionalNumber(filters.priceMin)
  const priceMax = parseOptionalNumber(filters.priceMax)
  const peMin = parseOptionalNumber(filters.peMin)
  const peMax = parseOptionalNumber(filters.peMax)
  const volumeMin = parseOptionalNumber(filters.volumeMin)
  const volumeMax = parseOptionalNumber(filters.volumeMax)
  const amountMin = parseOptionalNumber(filters.amountMin)
  const amountMax = parseOptionalNumber(filters.amountMax)
  const changePercentMin = parseOptionalNumber(filters.changePercentMin)
  const changePercentMax = parseOptionalNumber(filters.changePercentMax)
  const changeType = parseString(filters.changeType, 'any')
  const marketCapRange = parseString(filters.marketCapRange, 'any')

  return rows.filter((row) => {
    if (priceMin !== undefined && row.price < priceMin) return false
    if (priceMax !== undefined && row.price > priceMax) return false
    if (peMin !== undefined && row.pe < peMin) return false
    if (peMax !== undefined && row.pe > peMax) return false
    if (volumeMin !== undefined && row.volume < volumeMin) return false
    if (volumeMax !== undefined && row.volume > volumeMax) return false
    if (amountMin !== undefined && row.amount < amountMin) return false
    if (amountMax !== undefined && row.amount > amountMax) return false

    if (changeType === 'positive' && row.changePercent < 0) return false
    if (changeType === 'negative' && row.changePercent > 0) return false
    if (changePercentMin !== undefined && row.changePercent < changePercentMin) return false
    if (changePercentMax !== undefined && row.changePercent > changePercentMax) return false

    if (marketCapRange === 'large' && row.marketCap <= 50_000_000_000) return false
    if (marketCapRange === 'mid' && (row.marketCap < 5_000_000_000 || row.marketCap > 50_000_000_000)) return false
    if (marketCapRange === 'small' && row.marketCap >= 5_000_000_000) return false

    return true
  })
}
