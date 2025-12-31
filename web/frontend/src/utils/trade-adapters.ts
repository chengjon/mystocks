/**
 * Trade Management Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  OrderResponse,
  TradeHistoryResponse
} from '@/api/types/generated-types'

// Temporary: Use any for missing generated types
// TODO: Fix type generation to include these types
type AccountOverviewResponse = any
type PositionResponse = any

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
    const todayPnLPercent = data.totalAssets ? (data.todayPnL / (data.totalAssets - data.todayPnL)) * 100 : 0
    const totalPnLPercent = data.totalAssets ? (data.totalPnL / (data.totalAssets - data.totalPnL)) * 100 : 0

    return {
      totalAssets: data.totalAssets || 0,
      availableCash: data.availableCash || 0,
      totalMarketValue: data.totalMarketValue || 0,
      totalPositionValue: data.totalPositionValue || 0,
      todayPnL: data.todayPnL || 0,
      todayPnLPercent: this.formatPercent(todayPnLPercent),
      totalPnL: data.totalPnL || 0,
      totalPnLPercent: this.formatPercent(totalPnLPercent),
      currency: data.currency || 'CNY',
      lastUpdate: Date.now(),
      assetAllocation: (data.assetAllocation || []).map(item => ({
        category: item.category || '',
        value: item.value || 0,
        percentage: this.formatPercent(item.percentage || 0),
        color: item.color || this.getColorForCategory(item.category)
      }))
    }
  }

  /**
   * Convert order response to ViewModel
   */
  static toOrderVM(data: OrderResponse[]): OrderVM[] {
    return data.map((order: any) => ({
      orderId: order.order_id || order.orderId || '',
      symbol: order.symbol || '',
      name: order.name || order.order_name || '',
      side: this.getOrderSide(order.side || order.order_side),
      type: order.type || order.order_type || 'market',
      quantity: order.quantity || order.order_quantity || 0,
      price: order.price || order.order_price || 0,
      amount: order.amount || order.order_amount || 0,
      status: this.getOrderStatus(order.status || order.order_status),
      filledQuantity: order.filledQuantity || order.filled_quantity || 0,
      filledAmount: order.filledAmount || order.filled_amount || 0,
      averagePrice: order.averagePrice || order.average_price || 0,
      orderTime: this.formatDateTime(order.orderTime || order.order_time),
      updateTime: this.formatDateTime(order.updateTime || order.update_time),
      remarks: order.remarks || order.order_remarks || ''
    }))
  }

  /**
   * Convert position response to ViewModel
   */
  static toPositionVM(data: PositionResponse[]): PositionVM[] {
    return data.map(position => {
      const unrealizedPnL = position.quantity && position.avgPrice && position.currentPrice
        ? (position.currentPrice - position.avgPrice) * position.quantity * (position.side === 'long' ? 1 : -1)
        : 0
      const unrealizedPnLPercent = position.costBasis ? (unrealizedPnL / position.costBasis) * 100 : 0
      const positionPnL = unrealizedPnL + (position.realizedPnL || 0)
      const positionPnLPercent = (position.costBasis ? (positionPnL / position.costBasis) * 100 : 0)

      return {
        symbol: position.symbol || '',
        name: position.name || '',
        side: (position.side || 'long') as 'long' | 'short',
        quantity: position.quantity || 0,
        avgPrice: position.avgPrice || 0,
        currentPrice: position.currentPrice || 0,
        marketValue: position.marketValue || 0,
        unrealizedPnL,
        unrealizedPnLPercent: this.formatPercent(unrealizedPnLPercent),
        realizedPnL: position.realizedPnL || 0,
        positionPnL,
        positionPnLPercent: this.formatPercent(positionPnLPercent),
        costBasis: position.costBasis || 0,
        marginUsed: position.marginUsed || 0,
        marginAvailable: position.marginAvailable || 0,
        lastUpdate: this.formatDateTime(position.lastUpdate)
      }
    })
  }

  /**
   * Convert trade history response to ViewModel
   */
  static toTradeHistoryVM(data: TradeHistoryResponse[]): TradeHistoryVM[] {
    // Group trades by date
    const groupedTrades = data.reduce((groups, trade: any) => {
      const date = this.formatDate(trade.tradeTime || trade.trade_time)
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(trade)
      return groups
    }, {} as Record<string, any[]>)

    // Convert to VMs
    return Object.entries(groupedTrades).map(([date, trades]) => {
      const tradesVM = trades.map(trade => this.toTradeVM(trade))
      const totalCommission = tradesVM.reduce((sum, trade) => sum + trade.commission, 0)
      const realizedPnL = tradesVM.reduce((sum, trade) => sum + trade.realizedPnL, 0)

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
  private static toTradeVM(trade: any): TradeVM {
    return {
      tradeId: trade.tradeId || '',
      orderId: trade.orderId || '',
      symbol: trade.symbol || '',
      name: trade.name || '',
      side: this.getOrderSide(trade.side),
      quantity: trade.quantity || 0,
      price: trade.price || 0,
      amount: trade.amount || 0,
      commission: trade.commission || 0,
      tradeTime: this.formatDateTime(trade.tradeTime),
      tradeType: trade.tradeType || 'T0',
      notes: trade.notes
    }
  }

  /**
   * Get order side
   */
  private static getOrderSide(side: string): 'buy' | 'sell' {
    return side?.toLowerCase() === 'sell' ? 'sell' : 'buy'
  }

  /**
   * Get order status
   */
  private static getOrderStatus(status: string): 'pending' | 'partial' | 'filled' | 'cancelled' | 'rejected' {
    switch (status?.toLowerCase()) {
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
  private static formatDateTime(timestamp: string | number | Date): string {
    const date = new Date(timestamp)
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
  private static formatDate(timestamp: string | number | Date): string {
    const date = new Date(timestamp)
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
