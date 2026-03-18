import { apiClient } from '@/api/apiClient.ts'
import type { UnifiedResponse } from '@/api/types/common.ts'

export const MARKET_DRAGON_TIGER_API_ROOT = '/v1/market/lhb'

export interface DragonTigerRecord {
  id: number
  symbol: string
  name: string
  trade_date: string
  reason?: string | null
  buy_amount: number
  sell_amount: number
  net_amount: number
  turnover_rate: number
  institution_buy?: number | null
  institution_sell?: number | null
  created_at?: string | null
}

export interface ListDragonTigerParams {
  tradeDate?: string
  limit?: number
}

export const dragonTigerService = {
  async listDragonTiger(params?: ListDragonTigerParams): Promise<UnifiedResponse<DragonTigerRecord[]>> {
    const requestParams: Record<string, unknown> = {
      limit: params?.limit ?? 20
    }

    if (params?.tradeDate) {
      requestParams.start_date = params.tradeDate
      requestParams.end_date = params.tradeDate
    }

    const response = await apiClient.get<DragonTigerRecord[] | UnifiedResponse<DragonTigerRecord[]>>(
      MARKET_DRAGON_TIGER_API_ROOT,
      {
        params: requestParams
      }
    )

    if (Array.isArray(response)) {
      return {
        success: true,
        code: 200,
        message: 'ok',
        data: response,
        timestamp: new Date().toISOString(),
        request_id: ''
      }
    }

    return response
  }
}

export default dragonTigerService
