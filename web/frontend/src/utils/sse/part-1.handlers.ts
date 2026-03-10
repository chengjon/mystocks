import type { SSEEvent } from './part-1.ts'

/**
 * Predefined SSE event handlers
 */
export const SSEHandlers = {
  /**
   * Handler for market data updates
   */
  marketData(
    callback: (data: { symbol: string; price: number; change: number }) => void
  ): (event: SSEEvent) => void {
    return (event: SSEEvent) => {
      if (event.event === 'market_update') {
        callback(event.data as { symbol: string; price: number; change: number })
      }
    }
  },

  /**
   * Handler for order updates
   */
  orderUpdate(
    callback: (data: { orderId: string; status: string; filled: number }) => void
  ): (event: SSEEvent) => void {
    return (event: SSEEvent) => {
      if (event.event === 'order_update') {
        callback(event.data as { orderId: string; status: string; filled: number })
      }
    }
  },

  /**
   * Handler for strategy updates
   */
  strategyUpdate(
    callback: (data: { strategyId: string; status: string; progress: number }) => void
  ): (event: SSEEvent) => void {
    return (event: SSEEvent) => {
      if (event.event === 'strategy_update') {
        callback(event.data as { strategyId: string; status: string; progress: number })
      }
    }
  },

  /**
   * Handler for system alerts
   */
  systemAlert(
    callback: (data: { id: string; severity: string; message: string }) => void
  ): (event: SSEEvent) => void {
    return (event: SSEEvent) => {
      if (event.event === 'system_alert') {
        callback(event.data as { id: string; severity: string; message: string })
      }
    }
  },

  /**
   * Handler for notifications
   */
  notification(
    callback: (data: { id: string; type: string; title: string; message: string }) => void
  ): (event: SSEEvent) => void {
    return (event: SSEEvent) => {
      if (event.event === 'notification') {
        callback(event.data as { id: string; type: string; title: string; message: string })
      }
    }
  }
}
