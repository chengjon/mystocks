import { request } from '@/utils/request.ts'
import { TradeAdapter } from '@/utils/trade-adapters.ts'
import {
  asNumber,
  asRecord,
  asString,
  normalizeAccountPayload,
  normalizeOrderRows,
  normalizePositionPayload,
  normalizeTradeRows,
  type ExecuteTradePayload,
  type StatisticsPayload,
  type TradeRouteEnvelope,
  unwrapResponseData,
} from './tradePayloadNormalization.ts'
import {
  downloadReconciliationResults,
  fetchReconciliationAccounts,
  fetchReconciliationResults,
  fetchReconciliationStatements,
  uploadReconciliationCsv,
} from './tradeReconciliation.ts'
import {
  fetchExecutionTracking,
  fetchExecutionTrackingDetail,
  postExternalExecutionTrigger,
  type ExecutionTrackingDetailPayload,
  type ExecutionTrackingPayload,
  type ExternalExecutionTriggerPayload,
  type ExternalExecutionTriggerRequest,
} from './tradeExecutionTracking.ts'
import type {
  ReconciliationAccountDescriptor,
  ReconciliationImportBatchPayload,
  ReconciliationImportSourceType,
  ReconciliationMatchStatus,
  ReconciliationResultsPayload,
  ReconciliationStatementsPayload,
} from './tradeReconciliation.ts'
import type {
  OrderRequest
// OrderResponse  // Currently unused
} from '@/api/types/additional-types.ts'
import type {
  OrderVM,
  PositionVM,
  AccountOverviewVM,
  TradeHistoryVM
} from '@/utils/trade-adapters.ts'
export type {
  BrokerReconciliationRow,
  ReconciliationAccountDescriptor,
  ReconciliationImportBatchPayload,
  ReconciliationImportSourceType,
  ReconciliationMatchStatus,
  ReconciliationResultRow,
  ReconciliationResultsPayload,
  ReconciliationStatementRow,
  ReconciliationStatementSummary,
  ReconciliationStatementsPayload,
} from './tradeReconciliation.ts'

const buildUnsupportedTradeActionError = (message: string): Error => new Error(message)

class TradeApiService {
  private baseUrl = '/api/trade'

  /**
   * Get account overview
   */
  async getAccountOverview(): Promise<AccountOverviewVM> {
    const rawData = await request.get(`${this.baseUrl}/portfolio`)
    return TradeAdapter.toAccountOverviewVM(normalizeAccountPayload(rawData))
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
    const query = {
      symbol: params?.symbol,
      page_size: params?.limit,
      start_date: params?.startDate,
      end_date: params?.endDate
    }
    const rawData = await request.get(`${this.baseUrl}/trades`, { params: query })
    return TradeAdapter.toOrderVM(normalizeOrderRows(rawData))
  }

  /**
   * Get order details
   */
  async getOrder(orderId: string): Promise<OrderVM> {
    const orders = await this.getOrders({ limit: 200 })
    const matchedOrder = orders.find((item) => item.orderId === orderId)

    if (!matchedOrder) {
      throw new Error(`未找到委托记录: ${orderId}`)
    }

    return matchedOrder
  }

  /**
   * Create a new order
   */
  async createOrder(orderData: OrderRequest): Promise<OrderVM> {
    const payload = {
      symbol: orderData.symbol,
      direction: orderData.side || 'buy',
      order_type: orderData.type || 'limit',
      quantity: orderData.quantity,
      price: orderData.price
    }

    const rawData = await request.post(`${this.baseUrl}/execute`, payload)
    const response = unwrapResponseData<ExecuteTradePayload>(rawData)
    const order = response?.data?.order || payload

    return TradeAdapter.toOrderVM([{
      order_id: response?.request_id || `execute-${Date.now()}`,
      symbol: order.symbol || payload.symbol,
      order_type: order.order_type || payload.order_type,
      direction: order.direction || payload.direction,
      quantity: order.quantity || payload.quantity,
      price: order.price || payload.price,
      status: 'pending',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }])[0]
  }

  /**
   * Cancel order
   */
  async cancelOrder(orderId: string): Promise<void> {
    throw buildUnsupportedTradeActionError(`当前后端未提供委托撤销接口: ${orderId}`)
  }

  /**
   * Modify order
   */
  async modifyOrder(orderId: string, modifications: {
    quantity?: number
    price?: number
  }): Promise<OrderVM> {
    throw buildUnsupportedTradeActionError(
      `当前后端未提供委托改单接口: ${orderId} (${JSON.stringify(modifications)})`
    )
  }

  /**
   * Get all positions
   */
  async getPositions(params?: {
    symbol?: string
    side?: string
  }): Promise<PositionVM[]> {
    const rawData = await request.get(`${this.baseUrl}/positions`, { params })
    const positions = TradeAdapter.toPositionVM(normalizePositionPayload(rawData))
    if (params?.symbol) {
      return positions.filter((item) => item.symbol === params.symbol)
    }
    return positions
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
    const positions = await this.getPositions({ symbol })
    if (positions.length === 0) {
      throw new Error(`未找到持仓: ${symbol}`)
    }
    return positions[0]
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
    page?: number
    pageSize?: number
  }): Promise<TradeHistoryVM[]> {
    const query = {
      symbol: params?.symbol,
      start_date: params?.startDate,
      end_date: params?.endDate,
      page: params?.page,
      page_size: params?.pageSize || params?.limit
    }
    const rawData = await request.get(`${this.baseUrl}/trades`, { params: query })
    return TradeAdapter.toTradeHistoryVM(normalizeTradeRows(rawData))
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
    const [accountOverview, positions] = await Promise.all([
      this.getAccountOverview(),
      this.getPositions()
    ])

    const totalExposure = positions.reduce((sum, position) => sum + asNumber(position.marketValue), 0)
    const totalAssets = asNumber(accountOverview.totalAssets)
    const freeMargin = asNumber(accountOverview.availableCash)
    const marginRequirement = totalExposure
    const leverage = totalAssets > 0 ? totalExposure / totalAssets : 0
    const exposureRatio = totalAssets > 0 ? totalExposure / totalAssets : 0

    let riskLevel: 'low' | 'medium' | 'high' = 'low'
    if (exposureRatio >= 0.8 || leverage >= 0.8) {
      riskLevel = 'high'
    } else if (exposureRatio >= 0.5 || leverage >= 0.5) {
      riskLevel = 'medium'
    }

    return {
      totalExposure,
      marginRequirement,
      freeMargin,
      leverage,
      riskLevel
    }
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
    const rawData = await request.get(`${this.baseUrl}/statistics`, {
      params: { period }
    })
    const payload = unwrapResponseData<TradeRouteEnvelope<StatisticsPayload>>(rawData)
    const statistics = asRecord(payload?.statistics)
    const totalTrades = asNumber(statistics.total_trades)
    const buyCount = asNumber(statistics.buy_count)
    const sellCount = asNumber(statistics.sell_count)
    const realizedProfit = asNumber(statistics.realized_profit)

    return {
      totalTrades,
      winningTrades: buyCount,
      losingTrades: sellCount,
      winRate: totalTrades > 0 ? (buyCount / totalTrades) * 100 : 0,
      avgWin: buyCount > 0 ? realizedProfit / buyCount : 0,
      avgLoss: sellCount > 0 ? Math.abs(realizedProfit) / sellCount : 0,
      profitFactor: sellCount > 0 ? buyCount / sellCount : buyCount > 0 ? buyCount : 0,
      totalCommission: asNumber(statistics.total_commission)
    }
  }

  async getReconciliationAccounts(): Promise<ReconciliationAccountDescriptor[]> {
    return fetchReconciliationAccounts()
  }

  async getReconciliationStatements(params: {
    accountId: string
    startDate?: string
    endDate?: string
    page?: number
    pageSize?: number
  }): Promise<ReconciliationStatementsPayload> {
    return fetchReconciliationStatements(params)
  }

  async importReconciliationCsv(params: {
    file: File
    sourceType: ReconciliationImportSourceType
    accountId?: string
  }): Promise<ReconciliationImportBatchPayload> {
    return uploadReconciliationCsv(params)
  }

  async getReconciliationResults(params: {
    accountId: string
    importBatchId: string
    startDate?: string
    endDate?: string
    matchStatus?: ReconciliationMatchStatus
    page?: number
    pageSize?: number
  }): Promise<ReconciliationResultsPayload> {
    return fetchReconciliationResults(params)
  }

  async exportReconciliationResults(params: {
    accountId: string
    importBatchId: string
    startDate?: string
    endDate?: string
    matchStatus?: ReconciliationMatchStatus
  }): Promise<Blob> {
    return downloadReconciliationResults(params)
  }

  async getExecutionTracking(params?: {
    accountId?: string
    orderId?: string
    bridgeTaskId?: string
    page?: number
    pageSize?: number
  }): Promise<ExecutionTrackingPayload> {
    return fetchExecutionTracking(params)
  }

  async getExecutionTrackingDetail(trackingId: string): Promise<ExecutionTrackingDetailPayload> {
    return fetchExecutionTrackingDetail(trackingId)
  }

  async triggerExternalExecution(
    params: ExternalExecutionTriggerRequest,
  ): Promise<ExternalExecutionTriggerPayload> {
    return postExternalExecutionTrigger(params)
  }

  /**
   * Batch cancel orders
   */
  async batchCancelOrders(orderIds: string[]): Promise<{
    cancelled: string[]
    failed: Array<{ orderId: string; reason: string }>
  }> {
    return {
      cancelled: [],
      failed: orderIds.map((orderId) => ({
        orderId,
        reason: '当前后端未提供批量撤单接口'
      }))
    }
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
    const errors: string[] = []
    const warnings: string[] = []
    const quantity = asNumber(orderData.quantity)
    const price = asNumber(orderData.price)

    if (!asString(orderData.symbol).trim()) {
      errors.push('股票代码不能为空')
    }

    if (!orderData.side || !['buy', 'sell'].includes(orderData.side)) {
      errors.push('交易方向无效')
    }

    if (!orderData.type || !['market', 'limit', 'stop'].includes(orderData.type)) {
      errors.push('订单类型无效')
    }

    if (quantity <= 0) {
      errors.push('委托数量必须大于 0')
    }

    if (orderData.type !== 'market' && price <= 0) {
      errors.push('限价/止损委托必须提供有效价格')
    }

    if (orderData.type === 'market' && price <= 0) {
      warnings.push('市价单未提供价格，预估成交金额将按 0 计算')
    }

    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined,
      warnings: warnings.length > 0 ? warnings : undefined,
      estimatedCost: quantity * Math.max(price, 0)
    }
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
    throw buildUnsupportedTradeActionError(`当前后端未提供委托执行状态接口: ${orderId}`)
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
    return {
      canTrade: true,
      canShortSell: false,
      canTradeOptions: false,
      maxLeverage: 1,
      maxOrderSize: 0,
      maxPositionSize: 0
    }
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
    return response as Blob
  }
}

// Export singleton instance
export const tradeApi = new TradeApiService()

// Export class for dependency injection
export default TradeApiService
