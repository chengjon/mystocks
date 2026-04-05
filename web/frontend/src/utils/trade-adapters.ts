/**
 * Trade Management Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  OrderResponse,
  TradeHistoryResponse
} from '@/api/types/generated-types.ts'

// Temporary: Use any for missing generated types
// TODO: Fix type generation to include these types
type AccountOverviewResponse = Record<string, unknown>
type PositionResponse = Record<string, unknown>
type AnyRecord = Record<string, unknown>

const asRecord = (value: unknown): AnyRecord =>
  typeof value === 'object' && value !== null ? (value as AnyRecord) : {}

const asArray = <T = unknown>(value: unknown): T[] =>
  Array.isArray(value) ? (value as T[]) : []

const asString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : value == null ? fallback : String(value)

const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback

// ViewModel interfaces
export interface AccountOverviewVM {
  totalAssets: number
  availableCash: number
  totalMarketValue: number
  totalPositionValue: number
  todayPnL: number
  todayPnLPercent: string
  totalPnL: number
  totalPnLPercent: string
  currency: string
  lastUpdate: number
  assetAllocation: AssetAllocationVM[]
}

export interface AssetAllocationVM {
  category: string
  value: number
  percentage: string
  color: string
}

export interface OrderVM {
  orderId: string
  symbol: string
  name: string
  side: 'buy' | 'sell'
  type: string
  quantity: number
  price: number
  amount: number
  status: 'pending' | 'partial' | 'filled' | 'cancelled' | 'rejected'
  filledQuantity: number
  filledAmount: number
  averagePrice: number
  orderTime: string
  updateTime: string
  remarks?: string
}

export interface PositionVM {
  symbol: string
  name: string
  side: 'long' | 'short'
  quantity: number
  avgPrice: number
  currentPrice: number
  marketValue: number
  unrealizedPnL: number
  unrealizedPnLPercent: string
  realizedPnL: number
  positionPnL: number
  positionPnLPercent: string
  costBasis: number
  marginUsed: number
  marginAvailable: number
  lastUpdate: string
}

export interface TradeVM {
  tradeId: string
  orderId: string
  symbol: string
  name: string
  side: 'buy' | 'sell'
  quantity: number
  price: number
  amount: number
  commission: number
  tradeTime: string
  tradeType: string
  realizedPnL?: number
  notes?: string
}

export interface TradeHistoryVM {
  date: string
  trades: TradeVM[]
  totalTrades: number
  totalVolume: number
  totalCommission: number
  realizedPnL: number
}

export class TradeAdapter {
  /**
   * Convert account overview to ViewModel
   */
  static toAccountOverviewVM(data: AccountOverviewResponse): AccountOverviewVM {
    const totalAssets = asNumber(data.totalAssets)
    const todayPnL = asNumber(data.todayPnL)
    const totalPnL = asNumber(data.totalPnL)
    const todayPnLPercent = totalAssets ? (todayPnL / (totalAssets - todayPnL)) * 100 : 0
    const totalPnLPercent = totalAssets ? (totalPnL / (totalAssets - totalPnL)) * 100 : 0

    return {
      totalAssets,
      availableCash: asNumber(data.availableCash),
      totalMarketValue: asNumber(data.totalMarketValue),
      totalPositionValue: asNumber(data.totalPositionValue),
      todayPnL,
      todayPnLPercent: this.formatPercent(todayPnLPercent),
      totalPnL,
      totalPnLPercent: this.formatPercent(totalPnLPercent),
      currency: asString(data.currency, 'CNY'),
      lastUpdate: Date.now(),
      assetAllocation: asArray(data.assetAllocation).map((item) => {
        const record = asRecord(item)
        return {
          category: asString(record.category),
          value: asNumber(record.value),
          percentage: this.formatPercent(asNumber(record.percentage)),
          color: asString(record.color, this.getColorForCategory(asString(record.category)))
        }
      })
    }
  }

  /**
   * Convert order response to ViewModel
   */
  static toOrderVM(data: OrderResponse[]): OrderVM[] {
    return data.map((order) => {
      const record = asRecord(order)
      return {
        orderId: asString(record.order_id || record.orderId),
        symbol: asString(record.symbol),
        name: asString(record.name || record.order_name),
        side: this.getOrderSide(record.side || record.order_side || record.direction),
        type: asString(record.type || record.order_type, 'market'),
        quantity: asNumber(record.quantity || record.order_quantity),
        price: asNumber(record.price || record.order_price),
        amount: asNumber(record.amount || record.order_amount),
        status: this.getOrderStatus(record.status || record.order_status),
        filledQuantity: asNumber(record.filledQuantity || record.filled_quantity),
        filledAmount: asNumber(record.filledAmount || record.filled_amount),
        averagePrice: asNumber(record.averagePrice || record.average_price),
        orderTime: this.formatDateTime(record.orderTime || record.order_time || record.created_at),
        updateTime: this.formatDateTime(record.updateTime || record.update_time || record.updated_at),
        remarks: asString(record.remarks || record.order_remarks) || undefined
      }
    })
  }

  /**
   * Convert position response to ViewModel
   */
  static toPositionVM(data: PositionResponse[]): PositionVM[] {
    return data.map(position => {
      const record = asRecord(position)
      const quantity = asNumber(record.quantity)
      const avgPrice = asNumber(record.avgPrice)
      const currentPrice = asNumber(record.currentPrice)
      const side = (asString(record.side, 'long') as 'long' | 'short')
      const unrealizedPnL = quantity && avgPrice && currentPrice
        ? (currentPrice - avgPrice) * quantity * (side === 'long' ? 1 : -1)
        : 0
      const costBasis = asNumber(record.costBasis)
      const realizedPnL = asNumber(record.realizedPnL)
      const unrealizedPnLPercent = costBasis ? (unrealizedPnL / costBasis) * 100 : 0
      const positionPnL = unrealizedPnL + realizedPnL
      const positionPnLPercent = costBasis ? (positionPnL / costBasis) * 100 : 0

      return {
        symbol: asString(record.symbol),
        name: asString(record.name),
        side,
        quantity,
        avgPrice,
        currentPrice,
        marketValue: asNumber(record.marketValue),
        unrealizedPnL,
        unrealizedPnLPercent: this.formatPercent(unrealizedPnLPercent),
        realizedPnL,
        positionPnL,
        positionPnLPercent: this.formatPercent(positionPnLPercent),
        costBasis,
        marginUsed: asNumber(record.marginUsed),
        marginAvailable: asNumber(record.marginAvailable),
        lastUpdate: this.formatDateTime(record.lastUpdate)
      }
    })
  }

  /**
   * Convert trade history response to ViewModel
   */
  static toTradeHistoryVM(data: TradeHistoryResponse[]): TradeHistoryVM[] {
    // Group trades by date
    const groupedTrades = data.reduce((groups, trade) => {
      const record = asRecord(trade)
      const date = this.formatDate(record.tradeTime || record.trade_time || record.trade_date)
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(record)
      return groups
    }, {} as Record<string, unknown[]>)

    // Convert to VMs
    return Object.entries(groupedTrades).map(([date, trades]) => {
      const tradesVM = trades.map(trade => this.toTradeVM(trade))
      const totalCommission = tradesVM.reduce((sum, trade) => sum + trade.commission, 0)
      const realizedPnL = tradesVM.reduce((sum, trade) => sum + (trade.realizedPnL ?? 0), 0)

      return {
        date,
        trades: tradesVM,
        totalTrades: trades.length,
        totalVolume: tradesVM.reduce((sum, trade) => sum + trade.amount, 0),
        totalCommission,
        realizedPnL
      }
    })
  }

  /**
   * Convert single trade to ViewModel
   */
  private static toTradeVM(trade: unknown): TradeVM {
    const record = asRecord(trade)
    return {
      tradeId: asString(record.tradeId || record.trade_id),
      orderId: asString(record.orderId || record.order_id),
      symbol: asString(record.symbol),
      name: asString(record.name),
      side: this.getOrderSide(record.side || record.action),
      quantity: asNumber(record.quantity),
      price: asNumber(record.price),
      amount: asNumber(record.amount),
      commission: asNumber(record.commission),
      tradeTime: this.formatDateTime(record.tradeTime || record.trade_time || record.trade_date),
      tradeType: asString(record.tradeType || record.trade_type || 'T0'),
      notes: asString(record.notes) || undefined,
      realizedPnL: typeof record.realizedPnL === 'number' ? record.realizedPnL : typeof record.profit_loss === 'number' ? record.profit_loss : undefined
    }
  }

  /**
   * Get order side
   */
  private static getOrderSide(side: unknown): 'buy' | 'sell' {
    return asString(side).toLowerCase() === 'sell' ? 'sell' : 'buy'
  }

  /**
   * Get order status
   */
  private static getOrderStatus(status: unknown): 'pending' | 'partial' | 'filled' | 'cancelled' | 'rejected' {
    switch (asString(status).toLowerCase()) {
      case 'new':
      case 'pending':
        return 'pending'
      case 'partial_filled':
        return 'partial'
      case 'filled':
        return 'filled'
      case 'cancelled':
        return 'cancelled'
      case 'rejected':
      case 'failed':
        return 'rejected'
      default:
        return 'pending'
    }
  }

  /**
   * Format percentage
   */
  private static formatPercent(value: number): string {
    const sign = value >= 0 ? '' : '-'
    return `${sign}${Math.abs(value).toFixed(2)}%`
  }

  /**
   * Format date and time
   */
  private static formatDateTime(timestamp: unknown): string {
    if (!timestamp) return ''
    const normalized = timestamp instanceof Date || typeof timestamp === 'string' || typeof timestamp === 'number'
      ? timestamp
      : asString(timestamp)
    const date = new Date(normalized)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Format date only
   */
  private static formatDate(timestamp: unknown): string {
    if (!timestamp) return ''
    const normalized = timestamp instanceof Date || typeof timestamp === 'string' || typeof timestamp === 'number'
      ? timestamp
      : asString(timestamp)
    const date = new Date(normalized)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  /**
   * Get color for asset category
   */
  private static getColorForCategory(category?: string): string {
    const colors: Record<string, string> = {
      'stock': '#409EFF',
      'bond': '#00BCD4',
      'fund': '#4CAF50',
      'futures': '#FF9800',
      'options': '#9C27B0',
      'cash': '#795548',
      'other': '#9E9E9E'
    }
    return colors[category?.toLowerCase() || 'other']
  }

  /**
   * Format currency
   */
  static formatCurrency(amount: number, currency: string = '¥'): string {
    return `${currency}${amount.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`
  }

  /**
   * Format large number
   */
  static formatLargeNumber(num: number): string {
    if (num >= 100000000) {
      return `${(num / 100000000).toFixed(1)}亿`
    } else if (num >= 10000) {
      return `${(num / 10000).toFixed(1)}万`
    }
    return num.toLocaleString()
  }

  /**
   * Get status color
   */
  static getStatusColor(status: string): string {
    switch (status) {
      case 'filled':
      case 'running':
        return '#67C23A'
      case 'pending':
      case 'partial':
        return '#E6A23C'
      case 'cancelled':
      case 'stopped':
        return '#909399'
      case 'rejected':
      case 'error':
        return '#F56C6C'
      default:
        return '#409EFF'
    }
  }
}

export default TradeAdapter
