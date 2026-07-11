import { request } from '@/utils/request.ts'

export interface WatchlistRecord {
  id: number
  name: string
  watchlist_type: string
  risk_profile: { risk_tolerance?: number }
  stocks_count: number
  is_active?: boolean
}

export interface WatchlistStockRecord {
  id?: number
  stock_code: string
  entry_price?: number | null
  current_price?: number | null
  entry_reason?: string | null
  stop_loss_price?: number | null
  target_price?: number | null
  weight?: number
  alerts_count?: number
}

export interface CreateWatchlistPayload {
  name: string
  watchlist_type: string
  risk_profile: { risk_tolerance?: number }
}

export interface UpdateWatchlistPayload {
  name?: string
  watchlist_type?: string
  risk_profile?: { risk_tolerance?: number }
  is_active?: boolean
}

export interface AddWatchlistStockPayload {
  stock_code: string
  entry_price?: number | null
  entry_reason?: string | null
  stop_loss_price?: number | null
  target_price?: number | null
  weight?: number
}

interface ServiceResponse<T> {
  success: boolean
  data: T
  message?: string
}

interface MonitoringRouteResponse<T> {
  success?: boolean
  data?: T
  message?: string
}

interface QuoteSnapshot {
  price: number
  isSynthetic: boolean
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object'
}

function isTransportWrapper(value: Record<string, unknown>): boolean {
  return 'status' in value || 'headers' in value || 'config' in value || 'statusText' in value
}

function isMonitoringRouteEnvelope(value: Record<string, unknown>): boolean {
  if ('success' in value || 'message' in value) {
    return true
  }

  return 'data' in value && !isTransportWrapper(value)
}

function extractTransportData(raw: unknown): unknown {
  if (!isRecord(raw)) {
    return raw
  }

  if ('data' in raw) {
    return raw.data
  }

  return raw
}

function extractMonitoringRouteResponse<T>(raw: unknown): MonitoringRouteResponse<T> | null {
  if (!isRecord(raw)) {
    return null
  }

  const nestedCandidate = isRecord(raw.data) ? raw.data : null
  if (nestedCandidate && isMonitoringRouteEnvelope(nestedCandidate)) {
    return nestedCandidate as MonitoringRouteResponse<T>
  }

  if (isMonitoringRouteEnvelope(raw)) {
    return raw as MonitoringRouteResponse<T>
  }

  return null
}

function extractMonitoringRouteData<T>(raw: unknown): T | undefined {
  const body = extractMonitoringRouteResponse<T>(raw)
  if (body) {
    return body.data
  }

  return extractTransportData(raw) as T | undefined
}

function toObjectRows(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return []
  }

  return value.filter((item): item is Record<string, unknown> => isRecord(item))
}

function extractCollectionRows(raw: unknown, collectionKeys: string[]): Record<string, unknown>[] {
  const payload = extractMonitoringRouteData<unknown>(raw)
  if (Array.isArray(payload)) {
    return toObjectRows(payload)
  }

  if (!isRecord(payload)) {
    return []
  }

  for (const key of collectionKeys) {
    const collection = payload[key]
    if (Array.isArray(collection)) {
      return toObjectRows(collection)
    }

    if (isRecord(collection)) {
      if (Array.isArray(collection.data)) {
        return toObjectRows(collection.data)
      }

      if (Array.isArray(collection.items)) {
        return toObjectRows(collection.items)
      }
    }
  }

  if (Array.isArray(payload.data)) {
    return toObjectRows(payload.data)
  }

  if (Array.isArray(payload.items)) {
    return toObjectRows(payload.items)
  }

  return []
}

function buildAlertCountMap(rows: Record<string, unknown>[]): Map<string, number> {
  const counts = new Map<string, number>()

  for (const row of rows) {
    const stockCode = typeof row.stock_code === 'string' ? row.stock_code : ''
    if (!stockCode) {
      continue
    }

    counts.set(stockCode, (counts.get(stockCode) ?? 0) + 1)
  }

  return counts
}

function buildQuoteSnapshotMap(rows: Record<string, unknown>[]): Map<string, QuoteSnapshot> {
  const snapshots = new Map<string, QuoteSnapshot>()

  for (const row of rows) {
    const symbol =
      typeof row.symbol === 'string'
        ? row.symbol
        : typeof row.stock_code === 'string'
          ? row.stock_code
          : ''
    const price = toOptionalNumber((row.current_price ?? row.currentPrice ?? row.price) as unknown)
    if (!symbol || price === undefined) {
      continue
    }

    const name = typeof row.name === 'string' ? row.name : ''
    snapshots.set(symbol, {
      price,
      isSynthetic: name === `股票${symbol}`,
    })
  }

  return snapshots
}

function resolveCurrentPrice(stock: WatchlistStockRecord, quote: QuoteSnapshot | undefined): number | null | undefined {
  if (quote) {
    if (quote.isSynthetic && stock.entry_price !== undefined && stock.entry_price !== null) {
      return stock.entry_price
    }

    return quote.price
  }

  return stock.current_price ?? stock.entry_price
}

function normalizeWatchlist(raw: unknown, index: number): WatchlistRecord {
  const record = (raw && typeof raw === 'object' ? raw : {}) as Record<string, unknown>
  const statistics = (
    record.statistics && typeof record.statistics === 'object'
      ? record.statistics
      : {}
  ) as Record<string, unknown>
  const inlineStockCount = Array.isArray(record.stocks) ? record.stocks.length : 0
  const explicitStockCount = toOptionalNumber(record.stocks_count)
  const derivedStockCount = toOptionalNumber(statistics.totalStocks)

  const normalized: WatchlistRecord = {
    id: Number(record.id ?? index + 1),
    name: typeof record.name === 'string' ? record.name : `Watchlist ${index + 1}`,
    watchlist_type: typeof record.watchlist_type === 'string' ? record.watchlist_type : 'manual',
    risk_profile: (record.risk_profile as { risk_tolerance?: number } | undefined) ?? {},
    stocks_count: explicitStockCount ?? (derivedStockCount && derivedStockCount > 0 ? derivedStockCount : inlineStockCount),
  }

  if (typeof record.is_active === 'boolean') {
    normalized.is_active = record.is_active
  }

  return normalized
}

function toOptionalNumber(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value)
    if (Number.isFinite(parsed)) {
      return parsed
    }
  }

  return undefined
}

function normalizeWatchlistStock(raw: unknown, index: number): WatchlistStockRecord {
  const record = (raw && typeof raw === 'object' ? raw : {}) as Record<string, unknown>
  const customFields = (
    record.customFields && typeof record.customFields === 'object'
      ? record.customFields
      : {}
  ) as Record<string, unknown>

  const alertsCount = Array.isArray(record.alerts)
    ? record.alerts.filter(alert => {
        if (!alert || typeof alert !== 'object') {
          return false
        }

        return (alert as Record<string, unknown>).isActive !== false
      }).length
    : toOptionalNumber(customFields.alerts_count ?? record.alerts_count)

  return {
    id: Number(record.id ?? index + 1),
    stock_code:
      typeof record.symbol === 'string'
        ? record.symbol
        : typeof record.stock_code === 'string'
          ? record.stock_code
          : '',
    entry_price: toOptionalNumber(customFields.entry_price ?? record.entry_price ?? record.entryPrice),
    current_price: toOptionalNumber(record.currentPrice ?? record.current_price),
    entry_reason:
      typeof record.notes === 'string'
        ? record.notes
        : typeof record.entry_reason === 'string'
          ? record.entry_reason
          : null,
    stop_loss_price: toOptionalNumber(
      customFields.stop_loss_price ?? record.stop_loss_price ?? record.stopLossPrice,
    ),
    target_price: toOptionalNumber(customFields.target_price ?? record.target_price ?? record.targetPrice),
    weight: toOptionalNumber(customFields.weight ?? record.weight),
    alerts_count: alertsCount,
  }
}

export const watchlistService = {
  async listWatchlists(): Promise<ServiceResponse<WatchlistRecord[]>> {
    const rawResponse = await request.get('/v1/monitoring/watchlists')
    const body = extractMonitoringRouteResponse<unknown>(rawResponse)
    const data = extractCollectionRows(rawResponse, ['watchlists', 'items', 'data'])

    return {
      success: body?.success ?? true,
      data: data.map((item, index) => normalizeWatchlist(item, index)),
      message: body?.message,
    }
  },

  async listWatchlistStocks(watchlistId: number): Promise<ServiceResponse<WatchlistStockRecord[]>> {
    const rawStocksResponse = await request.get(`/api/v1/monitoring/watchlists/${watchlistId}/stocks`)
    const body = extractMonitoringRouteResponse<unknown>(rawStocksResponse)
    const stocks = extractCollectionRows(rawStocksResponse, ['stocks', 'items', 'data']).map((item, index) =>
      normalizeWatchlistStock(item, index),
    )

    if (stocks.length === 0) {
      return {
        success: body?.success ?? true,
        data: [],
        message: body?.message,
      }
    }

    const symbols = [...new Set(stocks.map(stock => stock.stock_code).filter(Boolean))]
    const [rawAlertsResponse, rawQuotesResponse] = await Promise.all([
      request.get(`/api/v1/monitoring/analysis/portfolio/${watchlistId}/alerts`),
      request.get('/v1/market/quotes', {
        params: {
          symbols: symbols.join(','),
        },
      }),
    ])
    const alertCounts = buildAlertCountMap(extractCollectionRows(rawAlertsResponse, ['alerts', 'items', 'data']))
    const quoteSnapshots = buildQuoteSnapshotMap(extractCollectionRows(rawQuotesResponse, ['quotes', 'items', 'data']))

    return {
      success: body?.success ?? true,
      data: stocks.map((stock) => ({
        ...stock,
        current_price: resolveCurrentPrice(stock, quoteSnapshots.get(stock.stock_code)),
        alerts_count: alertCounts.get(stock.stock_code) ?? stock.alerts_count ?? 0,
      })),
      message: body?.message,
    }
  },

  async createWatchlist(payload: CreateWatchlistPayload): Promise<ServiceResponse<WatchlistRecord>> {
    const rawResponse = await request.post('/v1/monitoring/watchlists', payload)
    const body = extractMonitoringRouteResponse<unknown>(rawResponse)
    const created = extractMonitoringRouteData<unknown>(rawResponse)

    return {
      success: body?.success ?? true,
      data: normalizeWatchlist(created, 0),
      message: body?.message,
    }
  },

  async updateWatchlist(
    id: number,
    payload: UpdateWatchlistPayload,
  ): Promise<ServiceResponse<WatchlistRecord>> {
    const rawResponse = await request.put(`/api/v1/monitoring/watchlists/${id}`, payload)
    const body = extractMonitoringRouteResponse<unknown>(rawResponse)
    const updated = body?.data ?? rawResponse

    return {
      success: body?.success ?? true,
      data: normalizeWatchlist(updated, 0),
      message: body?.message,
    }
  },

  async deleteWatchlist(id: number): Promise<ServiceResponse<null>> {
    const rawResponse = await request.delete(`/api/v1/monitoring/watchlists/${id}`)
    const body = extractMonitoringRouteResponse<null>(rawResponse)

    return {
      success: body?.success ?? true,
      data: null,
      message: body?.message,
    }
  },

  async addStockToWatchlist(watchlistId: number, payload: AddWatchlistStockPayload): Promise<ServiceResponse<null>> {
    const rawResponse = await request.post(`/api/v1/monitoring/watchlists/${watchlistId}/stocks`, payload)
    const body = extractMonitoringRouteResponse<null>(rawResponse)

    return {
      success: body?.success ?? true,
      data: null,
      message: body?.message,
    }
  },

  async removeStockFromWatchlist(watchlistId: number, stockCode: string): Promise<ServiceResponse<null>> {
    const rawResponse = await request.delete(`/api/v1/monitoring/watchlists/${watchlistId}/stocks/${stockCode}`)
    const body = extractMonitoringRouteResponse<null>(rawResponse)

    return {
      success: body?.success ?? true,
      data: null,
      message: body?.message,
    }
  }
}
