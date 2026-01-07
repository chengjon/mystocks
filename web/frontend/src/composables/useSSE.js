/**
 * SSE (Server-Sent Events) Composable for Vue 3
 * Week 2 Day 3 - SSE Real-time Push Frontend Integration
 *
 * Provides reactive SSE connection management for real-time updates
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { API_BASE_URL } from '@/config/api.js'

/**
 * Base SSE composable for generic SSE connections
 *
 * @param {string} url - SSE endpoint URL
 * @param {Object} options - Configuration options
 * @param {string} options.clientId - Optional client identifier
 * @param {boolean} options.autoConnect - Auto-connect on mount (default: true)
 * @param {number} options.reconnectDelay - Initial reconnection delay in ms (default: 1000)
 * @param {number} options.maxReconnectDelay - Maximum reconnection delay in ms (default: 30000)
 * @param {number} options.maxRetries - Maximum reconnection attempts (default: Infinity)
 * @returns {Object} - Reactive SSE state and control methods
 */
export function useSSE(url, options = {}) {
  const {
    clientId = null,
    autoConnect = true,
    reconnectDelay = 1000,
    maxReconnectDelay = 30000,
    maxRetries = Infinity
  } = options

  // Reactive state
  const isConnected = ref(false)
  const error = ref(null)
  const lastEvent = ref(null)
  const connectionCount = ref(0)
  const retryCount = ref(0)

  // Internal state
  let eventSource = null
  let currentReconnectDelay = reconnectDelay
  let reconnectTimer = null
  let eventHandlers = new Map()

  /**
   * Build SSE URL with optional client_id parameter
   */
  const buildUrl = () => {
    // Prepend API_BASE_URL if url is relative (doesn't start with http)
    let fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`

    if (!clientId) return fullUrl
    const separator = fullUrl.includes('?') ? '&' : '?'
    return `${fullUrl}${separator}client_id=${clientId}`
  }

  /**
   * Connect to SSE endpoint
   */
  const connect = () => {
    if (eventSource) {
      console.warn('[SSE] Already connected or connecting')
      return
    }

    try {
      const sseUrl = buildUrl()
      console.log('[SSE] Connecting to SSE endpoint:', sseUrl)

      eventSource = new EventSource(sseUrl)

      // Connection opened
      eventSource.onopen = () => {
        console.log('[SSE] Connection opened')
        isConnected.value = true
        error.value = null
        connectionCount.value++
        retryCount.value = 0
        currentReconnectDelay = reconnectDelay

        if (reconnectTimer) {
          clearTimeout(reconnectTimer)
          reconnectTimer = null
        }
      }

      // Connection error
      eventSource.onerror = (e) => {
        console.error('[SSE] Connection error:', e)
        isConnected.value = false
        error.value = new Error('SSE connection failed')

        // Close current connection
        if (eventSource) {
          eventSource.close()
          eventSource = null
        }

        // Attempt reconnection with exponential backoff
        if (retryCount.value < maxRetries) {
          retryCount.value++
          console.log(`[SSE] Reconnecting in ${currentReconnectDelay}ms (attempt ${retryCount.value}/${maxRetries})`)

          reconnectTimer = setTimeout(() => {
            currentReconnectDelay = Math.min(currentReconnectDelay * 2, maxReconnectDelay)
            connect()
          }, currentReconnectDelay)
        } else {
          console.error('[SSE] Max retries reached, giving up')
          error.value = new Error('Max reconnection attempts reached')
        }
      }

      // Register all event handlers
      eventHandlers.forEach((handler, eventType) => {
        eventSource.addEventListener(eventType, handler)
      })

    } catch (err) {
      console.error('[SSE] Failed to create EventSource:', err)
      error.value = err
      isConnected.value = false
    }
  }

  /**
   * Disconnect from SSE endpoint
   */
  const disconnect = () => {
    console.log('[SSE] Disconnecting...')

    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (eventSource) {
      eventSource.close()
      eventSource = null
    }

    isConnected.value = false
    retryCount.value = 0
    currentReconnectDelay = reconnectDelay
  }

  /**
   * Add event listener for specific event type
   *
   * @param {string} eventType - Event type to listen for
   * @param {Function} handler - Event handler function
   */
  const addEventListener = (eventType, handler) => {
    const wrappedHandler = (event) => {
      try {
        const data = JSON.parse(event.data)
        lastEvent.value = { eventType, data, timestamp: new Date() }
        handler(data)
      } catch (err) {
        console.error(`[SSE] Failed to parse event data for ${eventType}:`, err)
      }
    }

    eventHandlers.set(eventType, wrappedHandler)

    // If already connected, register immediately
    if (eventSource) {
      eventSource.addEventListener(eventType, wrappedHandler)
    }
  }

  /**
   * Remove event listener for specific event type
   *
   * @param {string} eventType - Event type to remove
   */
  const removeEventListener = (eventType) => {
    const handler = eventHandlers.get(eventType)
    if (handler && eventSource) {
      eventSource.removeEventListener(eventType, handler)
    }
    eventHandlers.delete(eventType)
  }

  /**
   * Reset connection (disconnect and reconnect)
   */
  const reset = () => {
    disconnect()
    retryCount.value = 0
    error.value = null
    if (autoConnect) {
      connect()
    }
  }

  // Lifecycle hooks
  onMounted(() => {
    if (autoConnect) {
      connect()
    }
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    isConnected,
    error,
    lastEvent,
    connectionCount,
    retryCount,

    // Methods
    connect,
    disconnect,
    reset,
    addEventListener,
    removeEventListener
  }
}

/**
 * Training Progress SSE Composable
 * Monitors model training progress in real-time
 *
 * @param {Object} options - Configuration options
 * @returns {Object} - Training progress state and methods
 */
export function useTrainingProgress(options = {}) {
  const {
    clientId = `training-${Date.now()}`,
    autoConnect = true
  } = options

  const progress = ref(0)
  const status = ref('')
  const message = ref('')
  const metrics = ref({})
  const taskId = ref('')

  const sse = useSSE('/api/v1/sse/training', { clientId, autoConnect })

  // Handle connected event
  sse.addEventListener('connected', (data) => {
    console.log('[Training] Connected to training channel:', data)
  })

  // Handle training progress event
  sse.addEventListener('training_progress', (data) => {
    const progressData = data.data || data
    taskId.value = progressData.task_id || ''
    progress.value = progressData.progress || 0
    status.value = progressData.status || ''
    message.value = progressData.message || ''
    metrics.value = progressData.metrics || {}

    console.log('[Training] Progress update:', {
      taskId: taskId.value,
      progress: progress.value,
      status: status.value
    })
  })

  // Handle ping event (keepalive)
  sse.addEventListener('ping', (data) => {
    console.log('[Training] Keepalive ping received')
  })

  return {
    // SSE state
    ...sse,

    // Training-specific state
    taskId,
    progress,
    status,
    message,
    metrics
  }
}

/**
 * Backtest Progress SSE Composable
 * Monitors backtest execution progress in real-time
 *
 * @param {Object} options - Configuration options
 * @returns {Object} - Backtest progress state and methods
 */
export function useBacktestProgress(options = {}) {
  const {
    clientId = `backtest-${Date.now()}`,
    autoConnect = true
  } = options

  const progress = ref(0)
  const status = ref('')
  const message = ref('')
  const currentDate = ref('')
  const results = ref({})
  const backtestId = ref('')

  const sse = useSSE('/api/v1/sse/backtest', { clientId, autoConnect })

  // Handle connected event
  sse.addEventListener('connected', (data) => {
    console.log('[Backtest] Connected to backtest channel:', data)
  })

  // Handle backtest progress event
  sse.addEventListener('backtest_progress', (data) => {
    const progressData = data.data || data
    backtestId.value = progressData.backtest_id || ''
    progress.value = progressData.progress || 0
    status.value = progressData.status || ''
    message.value = progressData.message || ''
    currentDate.value = progressData.current_date || ''
    results.value = progressData.results || {}

    console.log('[Backtest] Progress update:', {
      backtestId: backtestId.value,
      progress: progress.value,
      status: status.value,
      currentDate: currentDate.value
    })
  })

  // Handle ping event (keepalive)
  sse.addEventListener('ping', (data) => {
    console.log('[Backtest] Keepalive ping received')
  })

  return {
    // SSE state
    ...sse,

    // Backtest-specific state
    backtestId,
    progress,
    status,
    message,
    currentDate,
    results
  }
}

/**
 * Risk Alerts SSE Composable
 * Monitors risk alert notifications in real-time
 *
 * @param {Object} options - Configuration options
 * @returns {Object} - Risk alerts state and methods
 */
export function useRiskAlerts(options = {}) {
  const {
    clientId = `alerts-${Date.now()}`,
    autoConnect = true,
    maxAlerts = 100  // Maximum alerts to keep in memory
  } = options

  const alerts = ref([])
  const latestAlert = ref(null)
  const unreadCount = ref(0)

  const sse = useSSE('/api/v1/sse/alerts', { clientId, autoConnect })

  // Handle connected event
  sse.addEventListener('connected', (data) => {
    console.log('[Alerts] Connected to alerts channel:', data)
  })

  // Handle risk alert event
  sse.addEventListener('risk_alert', (data) => {
    const alert = {
      ...(data.data || data),
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      read: false
    }

    // Add to alerts list
    alerts.value.unshift(alert)

    // Limit alerts in memory
    if (alerts.value.length > maxAlerts) {
      alerts.value = alerts.value.slice(0, maxAlerts)
    }

    // Update latest alert
    latestAlert.value = alert
    unreadCount.value++

    console.log('[Alerts] New risk alert:', alert)
  })

  // Handle ping event (keepalive)
  sse.addEventListener('ping', (data) => {
    console.log('[Alerts] Keepalive ping received')
  })

  /**
   * Mark alert as read
   */
  const markAsRead = (alertId) => {
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert && !alert.read) {
      alert.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  /**
   * Mark all alerts as read
   */
  const markAllAsRead = () => {
    alerts.value.forEach(alert => {
      alert.read = true
    })
    unreadCount.value = 0
  }

  /**
   * Clear all alerts
   */
  const clearAlerts = () => {
    alerts.value = []
    latestAlert.value = null
    unreadCount.value = 0
  }

  return {
    // SSE state
    ...sse,

    // Alerts-specific state
    alerts,
    latestAlert,
    unreadCount,

    // Alerts-specific methods
    markAsRead,
    markAllAsRead,
    clearAlerts
  }
}

/**
 * Dashboard Updates SSE Composable
 * Monitors real-time dashboard metrics updates
 *
 * @param {Object} options - Configuration options
 * @returns {Object} - Dashboard updates state and methods
 */
export function useDashboardUpdates(options = {}) {
  const {
    clientId = `dashboard-${Date.now()}`,
    autoConnect = true
  } = options

  const metrics = ref({})
  const updateType = ref('')
  const lastUpdate = ref(null)

  const sse = useSSE('/api/v1/sse/dashboard', { clientId, autoConnect })

  // Handle connected event
  sse.addEventListener('connected', (data) => {
    console.log('[Dashboard] Connected to dashboard channel:', data)
  })

  // Handle dashboard update event
  sse.addEventListener('dashboard_update', (data) => {
    const updateData = data.data || data
    updateType.value = updateData.update_type || ''
    metrics.value = updateData.data || {}
    lastUpdate.value = new Date()

    console.log('[Dashboard] Metrics update:', {
      updateType: updateType.value,
      metrics: metrics.value
    })
  })

  // Handle ping event (keepalive)
  sse.addEventListener('ping', (data) => {
    console.log('[Dashboard] Keepalive ping received')
  })

  return {
    // SSE state
    ...sse,

    // Dashboard-specific state
    metrics,
    updateType,
    lastUpdate
  }
}

export default {
  useSSE,
  useTrainingProgress,
  useBacktestProgress,
  useRiskAlerts,
  useDashboardUpdates
}
