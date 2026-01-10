/**
 * WebSocket Connection Manager
 *
 * Singleton pattern manager to maintain a single WebSocket connection
 * across all components, preventing connection explosion in multi-tab scenarios.
 *
 * Features:
 * - Singleton pattern (global unique connection)
 * - Multi-component subscription support
 * - Auto-reconnect with exponential backoff
 * - Heartbeat detection (30-second ping)
 * - Connection status management
 *
 * @version 1.0
 * @author Claude Code (Main CLI)
 * @date 2026-01-09
 */

type MessageHandler = (data: any) => void
type UnsubscribeFunction = () => void

interface WebSocketMessage {
  type: string
  data: any
  timestamp?: number
}

interface ConnectionStatus {
  isConnected: boolean
  isConnecting: boolean
  reconnectAttempts: number
  lastError?: string
  lastHeartbeat?: Date
}

class WebSocketManager {
  private static instance: WebSocketManager | null = null
  private ws: WebSocket | null = null
  private subscribers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 1000 // 1 second initial delay
  private heartbeatInterval: number | null = null
  private heartbeatTimeout: number = 30000 // 30 seconds

  private status: ConnectionStatus = {
    isConnected: false,
    isConnecting: false,
    reconnectAttempts: 0
  }

  private statusCallbacks: Set<(status: ConnectionStatus) => void> = new Set()

  private constructor() {
    this.connect()
  }

  /**
   * Get singleton instance
   */
  static getInstance(): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager()
    }
    return WebSocketManager.instance
  }

  /**
   * Establish WebSocket connection
   */
  private connect(): void {
    // Prevent multiple simultaneous connections
    if (this.status.isConnecting || this.status.isConnected) {
      return
    }

    this.status.isConnecting = true
    this.notifyStatusChange()

    // Read WebSocket URL from environment or use default
    const wsUrl = this.getWebSocketUrl()

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected')
        this.status.isConnected = true
        this.status.isConnecting = false
        this.reconnectAttempts = 0
        this.notifyStatusChange()

        // Start heartbeat
        this.startHeartbeat()
      }

      this.ws.onmessage = (event: MessageEvent) => {
        this.handleMessage(event)
      }

      this.ws.onclose = (event: CloseEvent) => {
        console.log('❌ WebSocket disconnected:', event.code, event.reason)
        this.status.isConnected = false
        this.status.isConnecting = false
        this.notifyStatusChange()

        // Stop heartbeat
        this.stopHeartbeat()

        // Attempt reconnection
        this.reconnect()
      }

      this.ws.onerror = (error: Event) => {
        console.error('WebSocket error:', error)
        this.status.lastError = 'WebSocket connection error'
        this.notifyStatusChange()
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.status.isConnecting = false
      this.status.lastError = String(error)
      this.notifyStatusChange()

      // Attempt reconnection
      this.reconnect()
    }
  }

  /**
   * Get WebSocket URL from environment
   */
  private getWebSocketUrl(): string {
    // Try to get from Vite env
    const viteWsUrl = import.meta.env.VITE_WS_BASE_URL
    if (viteWsUrl) {
      return viteWsUrl
    }

    // Fallback to location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/ws/market`
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)

      // Handle heartbeat ping
      if (message.type === 'pong') {
        this.status.lastHeartbeat = new Date()
        return
      }

      // Route message to subscribers
      const messageType = message.type || 'default'
      const handlers = this.subscribers.get(messageType)

      if (handlers && handlers.size > 0) {
        handlers.forEach(handler => {
          try {
            handler(message.data)
          } catch (error) {
            console.error(`Error in message handler for type "${messageType}":`, error)
          }
        })
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  /**
   * Auto-reconnect with exponential backoff
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnect attempts reached. Giving up.')
      this.status.lastError = 'Max reconnect attempts reached'
      this.notifyStatusChange()
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(
      `🔄 Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}, delay: ${delay}ms)`
    )

    this.status.reconnectAttempts = this.reconnectAttempts
    this.notifyStatusChange()

    setTimeout(() => {
      this.connect()
    }, delay)
  }

  /**
   * Start heartbeat detection (send ping every 30 seconds)
   */
  private startHeartbeat(): void {
    this.stopHeartbeat() // Clear existing interval if any

    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
      }
    }, this.heartbeatTimeout)
  }

  /**
   * Stop heartbeat detection
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Notify status change to all subscribers
   */
  private notifyStatusChange(): void {
    this.statusCallbacks.forEach(callback => {
      try {
        callback({ ...this.status })
      } catch (error) {
        console.error('Error in status callback:', error)
      }
    })
  }

  /**
   * Subscribe to a specific message type
   *
   * @param messageType - The type of message to subscribe to (e.g., 'market.quote', 'trade.signal')
   * @param callback - The callback function to handle incoming messages
   * @returns Unsubscribe function
   */
  subscribe(messageType: string, callback: MessageHandler): UnsubscribeFunction {
    // Initialize subscribers set for this message type if not exists
    if (!this.subscribers.has(messageType)) {
      this.subscribers.set(messageType, new Set())
    }

    // Add callback to subscribers
    this.subscribers.get(messageType)!.add(callback)

    console.log(`📝 Subscribed to "${messageType}" (total: ${this.subscribers.get(messageType)!.size})`)

    // Return unsubscribe function
    return () => {
      this.unsubscribe(messageType, callback)
    }
  }

  /**
   * Unsubscribe from a specific message type
   *
   * @param messageType - The type of message to unsubscribe from
   * @param callback - The callback function to remove
   */
  unsubscribe(messageType: string, callback: MessageHandler): void {
    const handlers = this.subscribers.get(messageType)
    if (handlers) {
      handlers.delete(callback)

      // Clean up if no more subscribers for this message type
      if (handlers.size === 0) {
        this.subscribers.delete(messageType)
        console.log(`🗑️  Cleaned up "${messageType}" (no more subscribers)`)
      } else {
        console.log(`📝 Unsubscribed from "${messageType}" (remaining: ${handlers.size})`)
      }
    }
  }

  /**
   * Subscribe to connection status changes
   *
   * @param callback - The callback function to handle status changes
   * @returns Unsubscribe function
   */
  onStatusChange(callback: (status: ConnectionStatus) => void): UnsubscribeFunction {
    this.statusCallbacks.add(callback)

    // Immediately call with current status
    callback({ ...this.status })

    return () => {
      this.statusCallbacks.delete(callback)
    }
  }

  /**
   * Send a message through WebSocket
   *
   * @param data - The data to send (will be JSON stringified)
   */
  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(data))
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
      }
    } else {
      console.warn('⚠️  WebSocket is not connected. Message not sent:', data)
    }
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    return { ...this.status }
  }

  /**
   * Manually close the WebSocket connection
   */
  close(): void {
    console.log('🔌 Closing WebSocket connection...')

    this.stopHeartbeat()

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.status.isConnected = false
    this.status.isConnecting = false
    this.notifyStatusChange()

    // Clear all subscribers
    this.subscribers.clear()

    // Reset singleton instance
    WebSocketManager.instance = null
  }

  /**
   * Force reconnection (useful for recovering from errors)
   */
  forceReconnect(): void {
    console.log('🔄 Force reconnecting...')

    this.close()
    this.reconnectAttempts = 0 // Reset attempts
    this.connect()
  }
}

// Export singleton instance
export default WebSocketManager

// Export types for TypeScript users
export type { MessageHandler, UnsubscribeFunction, ConnectionStatus, WebSocketMessage }

// Export convenience function for getting instance
export function getWebSocketManager(): WebSocketManager {
  return WebSocketManager.getInstance()
}
