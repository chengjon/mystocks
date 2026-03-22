import { userApi } from '@/api/user.ts'

export interface WatchlistRecord {
  id: number
  name: string
  watchlist_type: string
  risk_profile: { risk_tolerance?: number }
  stocks_count: number
}

export interface WatchlistStockRecord {
  stock_code: string
  entry_price?: number | null
  current_price?: number | null
  entry_reason?: string | null
  stop_loss_price?: number | null
  target_price?: number | null
  weight?: number
}

export interface CreateWatchlistPayload {
  name: string
  watchlist_type: string
  risk_profile: { risk_tolerance?: number }
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

function normalizeWatchlist(raw: unknown, index: number): WatchlistRecord {
  const record = (raw && typeof raw === 'object' ? raw : {}) as Record<string, unknown>
  return {
    id: Number(record.id ?? index + 1),
    name: typeof record.name === 'string' ? record.name : `Watchlist ${index + 1}`,
    watchlist_type: typeof record.watchlist_type === 'string' ? record.watchlist_type : 'manual',
    risk_profile: (record.risk_profile as { risk_tolerance?: number } | undefined) ?? {},
    stocks_count: typeof record.stocks_count === 'number' ? record.stocks_count : 0,
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

  async listWatchlistStocks(_watchlistId: number): Promise<ServiceResponse<WatchlistStockRecord[]>> {
    return { success: true, data: [] }
  },

  async createWatchlist(payload: CreateWatchlistPayload): Promise<ServiceResponse<WatchlistRecord>> {
    const created = await userApi.createWatchlist(payload as unknown as { name: string })
    return {
      success: true,
      data: normalizeWatchlist(created, 0),
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
