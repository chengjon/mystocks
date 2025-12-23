/**
 * Trade Management API Service
 *
 * Provides methods for managing trades, orders, and positions.
 */

import { request } from '@/utils/request'
import { TradeAdapter } from '@/utils/trade-adapters'
import type {
  OrderRequest,
  OrderResponse
} from '@/api/types/generated-types'
import type {
  OrderVM,
  PositionVM,
  AccountOverviewVM,
  TradeHistoryVM
} from '@/utils/trade-adapters'

class TradeApiService {
  private baseUrl = '/api/trade'

  /**
   * Get account overview
   */
  async getAccountOverview(): Promise<AccountOverviewVM> {
    const rawData = await request.get(`${this.baseUrl}/account`)
    return TradeAdapter.toAccountOverviewVM(rawData)
  }

  /**
   * Get all orders
   */
  async getOrders(params?: {
    symbol?: string
    status?: string
    side?: string
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<OrderVM[]> {
    const rawData = await request.get(`${this.baseUrl}/orders`, { params })
    return TradeAdapter.toOrderVM(rawData)
  }

  /**
   * Get order details
   */
  async getOrder(orderId: string): Promise<OrderVM> {
    const rawData = await request.get(`${this.baseUrl}/orders/${orderId}`)
    return TradeAdapter.toOrderVM([rawData])[0]
  }

  /**
   * Create a new order
   */
  async createOrder(orderData: OrderRequest): Promise<OrderVM> {
    const rawData = await request.post(`${this.baseUrl}/order`, orderData)
    return TradeAdapter.toOrderVM([rawData])[0]
  }

  /**
   * Cancel order
   */
  async cancelOrder(orderId: string): Promise<void> {
    await request.post(`${this.baseUrl}/orders/${orderId}/cancel`)
  }

  /**
   * Modify order
   */
  async modifyOrder(orderId: string, modifications: {
    quantity?: number
    price?: number
  }): Promise<OrderVM> {
    const rawData = await request.patch(`${this.baseUrl}/orders/${orderId}`, modifications)
    return TradeAdapter.toOrderVM([rawData])[0]
  }

  /**
   * Get all positions
   */
  async getPositions(params?: {
    symbol?: string
    side?: string
  }): Promise<PositionVM[]> {
    const rawData = await request.get(`${this.baseUrl}/positions`, { params })
    return TradeAdapter.toPositionVM(rawData)
  }

  /**
   * Close position
   */
  async closePosition(symbol: string, quantity?: number): Promise<void> {
    await request.post(`${this.baseUrl}/positions/${symbol}/close`, { quantity })
  }

  /**
   * Get position details
   */
  async getPosition(symbol: string): Promise<PositionVM> {
    const rawData = await request.get(`${this.baseUrl}/positions/${symbol}`)
    return TradeAdapter.toPositionVM([rawData])[0]
  }

  /**
   * Get trade history
   */
  async getTradeHistory(params?: {
    symbol?: string
    side?: string
    startDate?: string
    endDate?: string
    limit?: number
  }): Promise<TradeHistoryVM[]> {
    const rawData = await request.get(`${this.baseUrl}/history`, { params })
    return TradeAdapter.toTradeHistoryVM(rawData)
  }

  /**
   * Get order book
   */
  async getOrderBook(symbol: string, depth?: number): Promise<{
    bids: Array<[number, number]>
    asks: Array<[number, number]>
    timestamp: number
  }> {
    return request.get(`/api/market/orderbook/${symbol}`, {
      params: { depth }
    })
  }

  /**
   * Get recent trades
   */
  async getRecentTrades(symbol: string, limit?: number): Promise<Array<{
    price: number
    quantity: number
    time: number
    side: string
  }>> {
    return request.get(`/api/market/trades/${symbol}`, {
      params: { limit }
    })
  }

  /**
   * Get risk metrics
   */
  async getRiskMetrics(): Promise<{
    totalExposure: number
    marginRequirement: number
    freeMargin: number
    leverage: number
    riskLevel: 'low' | 'medium' | 'high'
  }> {
    return request.get(`${this.baseUrl}/risk-metrics`)
  }

  /**
   * Get trade statistics
   */
  async getTradeStatistics(period?: string): Promise<{
    totalTrades: number
    winningTrades: number
    losingTrades: number
    winRate: number
    avgWin: number
    avgLoss: number
    profitFactor: number
    totalCommission: number
  }> {
    return request.get(`${this.baseUrl}/statistics`, {
      params: { period }
    })
  }

  /**
   * Batch cancel orders
   */
  async batchCancelOrders(orderIds: string[]): Promise<{
    cancelled: string[]
    failed: Array<{ orderId: string; reason: string }>
  }> {
    return request.post(`${this.baseUrl}/orders/batch-cancel`, { orderIds })
  }

  /**
   * Validate order before submission
   */
  async validateOrder(orderData: OrderRequest): Promise<{
    valid: boolean
    errors?: string[]
    warnings?: string[]
    estimatedCost?: number
  }> {
    return request.post(`${this.baseUrl}/validate-order`, orderData)
  }

  /**
   * Get order execution status
   */
  async getExecutionStatus(orderId: string): Promise<{
    orderId: string
    status: string
    progress: number
    filledQuantity: number
    remainingQuantity: number
    avgPrice: number
  }> {
    return request.get(`${this.baseUrl}/execution/${orderId}`)
  }

  /**
   * Get trading permissions
   */
  async getTradingPermissions(): Promise<{
    canTrade: boolean
    canShortSell: boolean
    canTradeOptions: boolean
    maxLeverage: number
    maxOrderSize: number
    maxPositionSize: number
  }> {
    return request.get(`${this.baseUrl}/permissions`)
  }

  /**
   * Export trade records
   */
  async exportTrades(params?: {
    startDate?: string
    endDate?: string
    symbol?: string
    format?: 'csv' | 'excel' | 'json'
  }): Promise<Blob> {
    const response = await request.get(`${this.baseUrl}/export`, {
      params,
      responseType: 'blob'
    })
    return response
  }
}

// Export singleton instance
export const tradeApi = new TradeApiService()

// Export class for dependency injection
export default TradeApiService