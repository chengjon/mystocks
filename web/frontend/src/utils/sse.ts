
/**
 * Server-Sent Events Service
 *
 * Provides real-time updates from the backend with auto-reconnection and event filtering.
 */

export interface SSEOptions {
  url: string
  headers?: Record<string, string>
  retryInterval?: number
  maxRetries?: number
  timeout?: number
  withCredentials?: boolean
  filters?: SSEFilter[]
  heartbeat?: {
    interval: number
    timeout: number
  }
  stability?: {
    circuitBreakerThreshold?: number
    healthCheckInterval?: number
    connectionPoolSize?: number
    enableBackpressure?: boolean
  }
}

export interface SSEFilter {
  type?: string
  channel?: string
  data?: Record<string, any>
  handler?: (event: SSEEvent) => boolean
}

export interface SSEEvent {
  id?: string
  event: string
  data: any
  timestamp: number
  retry?: number
}

export interface SSEState {
  connected: boolean
  connecting: boolean
  reconnecting: boolean
  lastEventTime?: number
  retryCount: number
  error?: Error
}

type SSEEventHandler = (event: SSEEvent) => void
type SSEErrorHandler = (error: Error) => void
type SSEStateHandler = (state: SSEState) => void

/**
 * SSE Connection Manager
 */
export class SSEConnection {
  private eventSource?: EventSource
  private retryTimer?: NodeJS.Timeout
  private heartbeatTimer?: NodeJS.Timeout
  private heartbeatTimeout?: NodeJS.Timeout
  private subscriptions = new Map<string, Set<SSEEventHandler>>()
  private globalHandlers = new Set<SSEEventHandler>()
  private state: SSEState = {
    connected: false,
    connecting: false,
    reconnecting: false,
    retryCount: 0
  }

  constructor(private options: SSEOptions) {
    this.connect()
  }

  /**
   * Connect to SSE endpoint
   */
  connect(): void {
    if (this.state.connected || this.state.connecting) return

    this.state.connecting = true
    this.notifyStateChange()

    try {
      // Build URL with filters
      const url = this.buildURL()

      // Create EventSource
      this.eventSource = new EventSource(url, {
        withCredentials: this.options.withCredentials ?? true
      })

      // Setup event handlers
      this.eventSource.onopen = this.handleOpen.bind(this)
      this.eventSource.onmessage = this.handleMessage.bind(this)
      this.eventSource.onerror = this.handleError.bind(this)

      // Setup heartbeat
      if (this.options.heartbeat) {
        this.setupHeartbeat()
      }

      // Set timeout
      if (this.options.timeout) {
        setTimeout(() => {
          if (this.state.connecting) {
            this.handleError(new Error('Connection timeout'))
          }
        }, this.options.timeout)
      }
    } catch (error) {
      this.handleError(error as Error)
    }
  }

  /**
   * Disconnect from SSE endpoint
   */
  disconnect(): void {
    this.clearTimers()

    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = undefined
    }

    this.state.connected = false
    this.state.connecting = false
    this.state.reconnecting = false
    this.notifyStateChange()
  }

  /**
   * Subscribe to specific event type
   */
  subscribe(eventType: string, handler: SSEEventHandler): () => void {
    if (!this.subscriptions.has(eventType)) {
      this.subscriptions.set(eventType, new Set())
    }

    this.subscriptions.get(eventType)!.add(handler)

    // Return unsubscribe function
    return () => {
      const handlers = this.subscriptions.get(eventType)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.subscriptions.delete(eventType)
        }
      }
    }
  }

  /**
   * Subscribe to all events
   */
  onEvent(handler: SSEEventHandler): () => void {
    this.globalHandlers.add(handler)

    return () => {
      this.globalHandlers.delete(handler)
    }
  }

  /**
   * Subscribe to state changes
   */
  onStateChange(handler: SSEStateHandler): () => void {
    this.onStateChangeHandler = handler

    return () => {
      this.onStateChangeHandler = undefined
    }
  }

  /**
   * Subscribe to errors
   */
  onError(handler: SSEErrorHandler): () => void {
    this.errorHandlers.add(handler)

    return () => {
      this.errorHandlers.delete(handler)
    }
  }

  /**
   * Get current state
   */
  getState(): SSEState {
    return { ...this.state }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.state.connected
  }

  /**
   * Private methods
   */
  private buildURL(): string {
    const url = new URL(this.options.url, window.location.origin)

    // Add filters as query params
    if (this.options.filters && this.options.filters.length > 0) {
      const params = new URLSearchParams()
      this.options.filters.forEach((filter, index) => {
        if (filter.type) params.set(`filter[${index}][type]`, filter.type)
        if (filter.channel) params.set(`filter[${index}][channel]`, filter.channel)
        if (filter.data) {
          Object.entries(filter.data).forEach(([key, value]) => {
            params.set(`filter[${index}][data][${key}]`, String(value))
          })
        }
      })
      url.search = params.toString()
    }

    return url.toString()
  }

  private handleOpen(): void {
    this.state.connected = true
    this.state.connecting = false
    this.state.reconnecting = false
    this.state.retryCount = 0
    this.state.error = undefined

    this.notifyStateChange()
    this.startHeartbeat()
  }

  private handleMessage(event: MessageEvent): void {
    try {
      // Parse event data
      const sseEvent: SSEEvent = {
        id: event.lastEventId,
        event: event.type || 'message',
        data: JSON.parse(event.data),
        timestamp: Date.now(),
        retry: event.timeStamp ? Math.floor(event.timeStamp / 1000) : undefined  // timeStamp is milliseconds, retry needs seconds
      }

      this.state.lastEventTime = sseEvent.timestamp

      // Apply filters
      if (!this.passesFilters(sseEvent)) {
        return
      }

      // Notify global handlers
      this.globalHandlers.forEach(handler => {
        try {
          handler(sseEvent)
        } catch (error) {
          console.error('SSE: Error in global handler', error)
        }
      })

      // Notify specific handlers
      const handlers = this.subscriptions.get(sseEvent.event)
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(sseEvent)
          } catch (error) {
            console.error(`SSE: Error in ${sseEvent.event} handler`, error)
          }
        })
      }
    } catch (error) {
      console.error('SSE: Failed to parse message', error)
    }
  }

  private handleError(error: Event | Error): void {
    const errorObj = error instanceof Error ? error : new Error('SSE connection error')

    this.state.error = errorObj
    this.state.connected = false
    this.state.connecting = false

    this.notifyError(errorObj)
    this.notifyStateChange()

    // Attempt reconnection
    if (this.shouldRetry()) {
      this.scheduleRetry()
    }
  }

  private passesFilters(event: SSEEvent): boolean {
    if (!this.options.filters) return true

    return this.options.filters.every(filter => {
      if (filter.type && filter.type !== event.event) return false
      if (filter.handler && !filter.handler(event)) return false
      if (filter.data) {
        return Object.entries(filter.data).every(([key, value]) => {
          return event.data[key] === value
        })
      }
      return true
    })
  }

  private shouldRetry(): boolean {
    const maxRetries = this.options.maxRetries ?? 5
    return this.state.retryCount < maxRetries
  }

  private scheduleRetry(): void {
    this.state.reconnecting = true
    this.notifyStateChange()

    const retryInterval = this.options.retryInterval ?? 5000
    const delay = Math.min(retryInterval * Math.pow(2, this.state.retryCount), 30000)

    this.retryTimer = setTimeout(() => {
      this.state.retryCount++
      this.connect()
    }, delay)
  }

  private setupHeartbeat(): void {
    if (!this.options.heartbeat) return

    this.startHeartbeat()
  }

  private startHeartbeat(): void {
    if (!this.options.heartbeat || !this.state.connected) return

    this.clearHeartbeatTimers()

    // Expect heartbeat
    this.heartbeatTimeout = setTimeout(() => {
      console.warn('SSE: Heartbeat timeout')
      this.handleError(new Error('Heartbeat timeout'))
    }, this.options.heartbeat.timeout)
  }

  private clearHeartbeatTimers(): void {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout)
      this.heartbeatTimeout = undefined
    }
  }

  private clearTimers(): void {
    if (this.retryTimer) {
      clearTimeout(this.retryTimer)
      this.retryTimer = undefined
    }

    this.clearHeartbeatTimers()
  }

  private onStateChangeHandler?: SSEStateHandler
  private errorHandlers = new Set<SSEErrorHandler>()

  private notifyStateChange(): void {
    if (this.onStateChangeHandler) {
      try {
        this.onStateChangeHandler(this.getState())
      } catch (error) {
        console.error('SSE: Error in state change handler', error)
      }
    }
  }

  private notifyError(error: Error): void {
    this.errorHandlers.forEach(handler => {
      try {
        handler(error)
      } catch (e) {
        console.error('SSE: Error in error handler', e)
      }
    })
  }
}

/**
 * Global SSE Manager
 */
export class SSEManager {
  private static instance: SSEManager
  private connections = new Map<string, SSEConnection>()

  static getInstance(): SSEManager {
    if (!SSEManager.instance) {
      SSEManager.instance = new SSEManager()
    }
    return SSEManager.instance
  }

  create(name: string, options: SSEOptions): SSEConnection {
    // Close existing connection if any
    this.close(name)

    const connection = new SSEConnection(options)
    this.connections.set(name, connection)

    return connection
  }

  get(name: string): SSEConnection | undefined {
    return this.connections.get(name)
  }

  close(name: string): void {
    const connection = this.connections.get(name)
    if (connection) {
      connection.disconnect()
      this.connections.delete(name)
    }
  }

  closeAll(): void {
    this.connections.forEach(connection => connection.disconnect())
    this.connections.clear()
  }

  getAllStates(): Record<string, SSEState> {
    const states: Record<string, SSEState> = {}
    this.connections.forEach((connection, name) => {
      states[name] = connection.getState()
    })
    return states
  }
}

/**
 * Predefined SSE event handlers
 */
export const SSEHandlers = {
  /**
   * Handler for market data updates
   */
  marketData(callback: (data: { symbol: string; price: number; change: number }) => void) {
    return (event: SSEEvent) => {
      if (event.event === 'market_update') {
        callback(event.data)
      }
    }
  },

  /**
   * Handler for order updates
   */
  orderUpdate(callback: (data: { orderId: string; status: string; filled: number }) => void) {
    return (event: SSEEvent) => {
      if (event.event === 'order_update') {
        callback(event.data)
      }
    }
  },

  /**
   * Handler for strategy updates
   */
  strategyUpdate(callback: (data: { strategyId: string; status: string; progress: number }) => void) {
    return (event: SSEEvent) => {
      if (event.event === 'strategy_update') {
        callback(event.data)
      }
    }
  },

  /**
   * Handler for system alerts
   */
  systemAlert(callback: (data: { id: string; severity: string; message: string }) => void) {
    return (event: SSEEvent) => {
      if (event.event === 'system_alert') {
        callback(event.data)
      }
    }
  },

  /**
   * Handler for notifications
   */
  notification(callback: (data: { id: string; type: string; title: string; message: string }) => void) {
    return (event: SSEEvent) => {
      if (event.event === 'notification') {
        callback(event.data)
      }
    }
  }
}

/**
 * SSE Connection for Vue Composition API
 *
 * Note: This is a framework-agnostic utility. For Vue 3 integration,
 * use the SSEConnection class directly or create a Vue composable wrapper.
 *
 * Example Vue composable:
 * ```typescript
 * import { ref, onUnmounted } from 'vue'
 * import { SSEManager, type SSEOptions, type SSEEvent } from '@/utils/sse'
 *
 * export function useSSE(name: string, options: SSEOptions) {
 *   const connection = SSEManager.getInstance().create(name, options)
 *   const state = ref(connection.getState())
 *   const eventHandlers = new Map<string, Set<(event: SSEEvent) => void>>()
 *
 *   const unsubscribe = connection.onStateChange((newState) => {
 *     state.value = newState
 *   })
 *
 *   onUnmounted(() => {
 *     unsubscribe()
 *     SSEManager.getInstance().close(name)
 *   })
 *
 *   return {
 *     state: state.value,
 *     subscribe: (eventType: string, handler: (event: SSEEvent) => void) =>
 *       connection.subscribe(eventType, handler)
 *   }
 * }
 * ```
 */
export function useSSE(name: string, options: SSEOptions) {
  // This function is now a placeholder. See the documentation above
  // for how to create a Vue composable wrapper.
  console.warn('useSSE: This is a placeholder. Please implement a Vue composable wrapper.')
  return SSEManager.getInstance().create(name, options)
}

// Auto cleanup on page unload
window.addEventListener('beforeunload', () => {
  SSEManager.getInstance().closeAll()
})

export default SSEConnection
