import { apiDelete, apiGet, apiPost } from '@/api/apiClient.ts'
import type { UnifiedResponse } from '@/api/types/common.ts'

export const WATCHLIST_MANAGEMENT_API_ROOT = '/v1/monitoring/watchlists'

export interface WatchlistRecord {
  id: number
  name: string
  watchlist_type: string
  risk_profile?: { risk_tolerance?: number } | null
  is_active?: boolean
  created_at?: string
  updated_at?: string
  stocks_count?: number
}

export interface WatchlistStockRecord {
  id: number
  watchlist_id: number
  stock_code: string
  entry_price?: number | null
  current_price?: number | null
  entry_reason?: string | null
  stop_loss_price?: number | null
  target_price?: number | null
  weight?: number
  is_active?: boolean
}

export interface CreateWatchlistPayload {
  name: string
  watchlist_type: string
  risk_profile?: { risk_tolerance?: number }
}

export interface AddWatchlistStockPayload {
  stock_code: string
  entry_price?: number | null
  entry_reason?: string | null
  stop_loss_price?: number | null
  target_price?: number | null
  weight?: number
}

export const watchlistService = {
  listWatchlists(): Promise<UnifiedResponse<WatchlistRecord[]>> {
    return apiGet<UnifiedResponse<WatchlistRecord[]>>(WATCHLIST_MANAGEMENT_API_ROOT)
  },

  listWatchlistStocks(watchlistId: number): Promise<UnifiedResponse<WatchlistStockRecord[]>> {
    return apiGet<UnifiedResponse<WatchlistStockRecord[]>>(`${WATCHLIST_MANAGEMENT_API_ROOT}/${watchlistId}/stocks`)
  },

  createWatchlist(payload: CreateWatchlistPayload): Promise<UnifiedResponse<WatchlistRecord>> {
    return apiPost<UnifiedResponse<WatchlistRecord>>(WATCHLIST_MANAGEMENT_API_ROOT, payload)
  },

  deleteWatchlist(watchlistId: number): Promise<UnifiedResponse<null>> {
    return apiDelete<UnifiedResponse<null>>(`${WATCHLIST_MANAGEMENT_API_ROOT}/${watchlistId}`)
  },

  addStockToWatchlist(
    watchlistId: number,
    payload: AddWatchlistStockPayload
  ): Promise<UnifiedResponse<WatchlistStockRecord>> {
    return apiPost<UnifiedResponse<WatchlistStockRecord>>(
      `${WATCHLIST_MANAGEMENT_API_ROOT}/${watchlistId}/stocks`,
      payload
    )
  },

  removeStockFromWatchlist(watchlistId: number, stockCode: string): Promise<UnifiedResponse<null>> {
    return apiDelete<UnifiedResponse<null>>(`${WATCHLIST_MANAGEMENT_API_ROOT}/${watchlistId}/stocks/${stockCode}`)
  }
}

export default watchlistService
