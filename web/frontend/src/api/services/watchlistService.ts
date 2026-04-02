import { userApi } from '@/api/user.ts'
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

function extractMonitoringRouteResponse<T>(raw: unknown): MonitoringRouteResponse<T> | null {
  if (!raw || typeof raw !== 'object') {
    return null
  }

  const candidate = 'data' in raw ? (raw as { data?: unknown }).data : raw
  if (!candidate || typeof candidate !== 'object') {
    return null
  }

  return candidate as MonitoringRouteResponse<T>
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
    const data = await userApi.getWatchlists()
    return {
      success: true,
      data: data.map((item, index) => normalizeWatchlist(item, index)),
    }
  },

  async listWatchlistStocks(watchlistId: number): Promise<ServiceResponse<WatchlistStockRecord[]>> {
    const data = await userApi.getWatchlist(String(watchlistId))
    const stocks = Array.isArray(data.stocks) ? data.stocks : []

    return {
      success: true,
      data: stocks.map((item, index) => normalizeWatchlistStock(item, index)),
    }
  },

  async createWatchlist(payload: CreateWatchlistPayload): Promise<ServiceResponse<WatchlistRecord>> {
    const created = await userApi.createWatchlist(payload as unknown as { name: string })
    return {
      success: true,
      data: normalizeWatchlist(created, 0),
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
    await userApi.deleteWatchlist(String(id))
    return { success: true, data: null }
  },

  async addStockToWatchlist(watchlistId: number, payload: AddWatchlistStockPayload): Promise<ServiceResponse<null>> {
    await userApi.addStockToWatchlist(String(watchlistId), {
      symbol: payload.stock_code,
      notes: payload.entry_reason ?? undefined,
    })
    return { success: true, data: null }
  },

  async removeStockFromWatchlist(watchlistId: number, stockCode: string): Promise<ServiceResponse<null>> {
    await userApi.removeStockFromWatchlist(String(watchlistId), stockCode)
    return { success: true, data: null }
  }
}
