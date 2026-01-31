/**
 * WebSocket Connection Manager for Real-time Data
 * Handles connection lifecycle, reconnection, and message routing
 */

export interface WebSocketConfig {
  url: string
  protocols?: string[]
  reconnectAttempts?: number
  reconnectInterval?: number
  heartbeatInterval?: number
  timeout?: number
}

export interface WebSocketMessage {
  type: string
  channel?: string
  data?: any
  timestamp?: number
  id?: string
}

export type WebSocketEventHandler = (message: WebSocketMessage) => void
export type ConnectionStateHandler = (state: WebSocketState) => void

export enum WebSocketState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTING = 'disconnecting',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

class WebSocketManager {
  private ws: WebSocket | null = null
  private config: Required<WebSocketConfig>
  private state: WebSocketState = WebSocketState.DISCONNECTED
  private reconnectAttempts = 0
  private heartbeatTimer: number | null = null
  private reconnectTimer: number | null = null
  private eventHandlers = new Map<string, Set<WebSocketEventHandler>>()
  private connectionStateHandlers = new Set<ConnectionStateHandler>()

  constructor(config: WebSocketConfig) {
    this.config = {
      url: config.url,
      protocols: config.protocols || [],
      reconnectAttempts: config.reconnectAttempts || 5,
      reconnectInterval: config.reconnectInterval || 3000,
      heartbeatInterval: config.heartbeatInterval || 30000,
      timeout: config.timeout || 10000
    }
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.state === WebSocketState.CONNECTED || this.state === WebSocketState.CONNECTING) {
      return
    }

    this.updateState(WebSocketState.CONNECTING)

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.url, this.config.protocols)
        this.ws.binaryType = 'blob'

        const timeout = setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            this.ws.close()
            reject(new Error('WebSocket connection timeout'))
          }
        }, this.config.timeout)

        this.ws.onopen = () => {
          clearTimeout(timeout)
          this.updateState(WebSocketState.CONNECTED)
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(event)
        }

        this.ws.onclose = (event) => {
          clearTimeout(timeout)
          this.handleClose(event)
        }

        this.ws.onerror = (error) => {
          clearTimeout(timeout)
          this.handleError(error)
          reject(error)
        }

      } catch (error) {
        this.updateState(WebSocketState.ERROR)
        reject(error)
      }
    })
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.state === WebSocketState.DISCONNECTED) return

    this.updateState(WebSocketState.DISCONNECTING)
    this.stopHeartbeat()
    this.clearReconnectTimer()

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }

    this.updateState(WebSocketState.DISCONNECTED)
  }

  /**
   * Send message to WebSocket server
   */
  send(message: WebSocketMessage): boolean {
    if (this.state !== WebSocketState.CONNECTED || !this.ws) {
      console.warn('WebSocket is not connected, cannot send message:', message)
      return false
    }

    try {
      const messageToSend = {
        ...message,
        timestamp: Date.now(),
        id: message.id || this.generateId()
      }

      this.ws.send(JSON.stringify(messageToSend))
      return true
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
      return false
    }
  }

  /**
   * Subscribe to WebSocket events
   */
  on(event: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    this.eventHandlers.get(event)!.add(handler)
  }

  /**
   * Unsubscribe from WebSocket events
   */
  off(event: string, handler?: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(event)) return

    if (handler) {
      this.eventHandlers.get(event)!.delete(handler)
    } else {
      this.eventHandlers.delete(event)
    }
  }

  /**
   * Subscribe to connection state changes
   */
  onStateChange(handler: ConnectionStateHandler): void {
    this.connectionStateHandlers.add(handler)
  }

  /**
   * Unsubscribe from connection state changes
   */
  offStateChange(handler: ConnectionStateHandler): void {
    this.connectionStateHandlers.delete(handler)
  }

  /**
   * Get current connection state
   */
  getState(): WebSocketState {
    return this.state
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.state === WebSocketState.CONNECTED
  }

  private updateState(newState: WebSocketState): void {
    if (this.state === newState) return

    const oldState = this.state
    this.state = newState

    // Notify state change handlers
    this.connectionStateHandlers.forEach(handler => {
      try {
        handler(newState)
      } catch (error) {
        console.error('Error in connection state handler:', error)
      }
    })

    console.log(`WebSocket state changed: ${oldState} -> ${newState}`)
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)
      this.emit(message.type, message)
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error, event.data)
    }
  }

  private emit(event: string, message: WebSocketMessage): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error)
        }
      })
    }
  }

  private handleClose(event: CloseEvent): void {
    this.stopHeartbeat()
    this.ws = null

    const shouldReconnect = event.code !== 1000 && // Normal closure
                           this.reconnectAttempts < this.config.reconnectAttempts

    if (shouldReconnect) {
      this.attemptReconnect()
    } else {
      this.updateState(WebSocketState.DISCONNECTED)
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error)
    this.updateState(WebSocketState.ERROR)
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.reconnectAttempts) {
      console.error('Max reconnection attempts reached')
      this.updateState(WebSocketState.DISCONNECTED)
      return
    }

    this.reconnectAttempts++
    this.updateState(WebSocketState.RECONNECTING)

    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.reconnectAttempts})...`)

    this.reconnectTimer = window.setTimeout(async () => {
      try {
        await this.connect()
      } catch (error) {
        console.error('Reconnection failed:', error)
        this.attemptReconnect() // Try again
      }
    }, this.config.reconnectInterval)
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = window.setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'heartbeat' })
      }
    }, this.config.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private generateId(): string {
    return `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
}

// Global WebSocket manager instances
const marketDataWebSocket = new WebSocketManager({
  url: 'ws://localhost:8000/ws/market',
  reconnectAttempts: 10,
  reconnectInterval: 2000,
  heartbeatInterval: 30000
})

const tradingWebSocket = new WebSocketManager({
  url: 'ws://localhost:8000/ws/trading',
  reconnectAttempts: 5,
  reconnectInterval: 3000,
  heartbeatInterval: 30000
})

const riskWebSocket = new WebSocketManager({
  url: 'ws://localhost:8000/ws/risk',
  reconnectAttempts: 5,
  reconnectInterval: 3000,
  heartbeatInterval: 45000
})

export {
  WebSocketManager,
  marketDataWebSocket,
  tradingWebSocket,
  riskWebSocket
}

export default WebSocketManager