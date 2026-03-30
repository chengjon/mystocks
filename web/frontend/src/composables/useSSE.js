/**
 * SSE (Server-Sent Events) Composable for Vue 3
 * Week 2 Day 3 - SSE Real-time Push Frontend Integration
 *
 * Provides reactive SSE connection management for real-time updates
 */

import { ref, onMounted, onUnmounted, _watch } from 'vue'
import { API_BASE_URL } from '@/config/api.js'
import {
  appendBoundedAlert,
  clearAlertState,
  createChannelConnectedLogger,
  createKeepaliveLogger,
  createRiskAlertRecord,
  markAlertAsReadById,
  markAllAlertsAsRead,
  unwrapSSEPayload
} from './useSSE.helpers.js'

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
      void sseUrl

      eventSource = new globalThis.EventSource(sseUrl)

      // Connection opened
      eventSource.onopen = () => {
        isConnected.value = true
        error.value = null
        connectionCount.value++
        retryCount.value = 0
        currentReconnectDelay = reconnectDelay

        if (reconnectTimer) {
          globalThis.clearTimeout(reconnectTimer)
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

          reconnectTimer = globalThis.setTimeout(() => {
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
    if (reconnectTimer) {
      globalThis.clearTimeout(reconnectTimer)
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
  sse.addEventListener('connected', createChannelConnectedLogger('Training', 'training'))

  // Handle training progress event
  sse.addEventListener('training_progress', (data) => {
    const progressData = unwrapSSEPayload(data)
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
  sse.addEventListener('ping', createKeepaliveLogger('Training'))

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
  sse.addEventListener('connected', createChannelConnectedLogger('Backtest', 'backtest'))

  // Handle backtest progress event
  sse.addEventListener('backtest_progress', (data) => {
    const progressData = unwrapSSEPayload(data)
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
  sse.addEventListener('ping', createKeepaliveLogger('Backtest'))

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
  sse.addEventListener('connected', createChannelConnectedLogger('Alerts', 'alerts'))

  // Handle risk alert event
  sse.addEventListener('risk_alert', (data) => {
    const alert = createRiskAlertRecord(data)
    appendBoundedAlert(alerts, alert, maxAlerts)

    // Update latest alert
    latestAlert.value = alert
    unreadCount.value++

    console.log('[Alerts] New risk alert:', alert)
  })

  // Handle ping event (keepalive)
  sse.addEventListener('ping', createKeepaliveLogger('Alerts'))

  /**
   * Mark alert as read
   */
  const markAsRead = (alertId) => {
    markAlertAsReadById(alerts, unreadCount, alertId)
  }

  /**
   * Mark all alerts as read
   */
  const markAllAsRead = () => {
    markAllAlertsAsRead(alerts, unreadCount)
  }

  /**
   * Clear all alerts
   */
  const clearAlerts = () => {
    clearAlertState(alerts, latestAlert, unreadCount)
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
  sse.addEventListener('connected', createChannelConnectedLogger('Dashboard', 'dashboard'))

  // Handle dashboard update event
  sse.addEventListener('dashboard_update', (data) => {
    const updateData = unwrapSSEPayload(data)
    updateType.value = updateData.update_type || ''
    metrics.value = updateData.data || {}
    lastUpdate.value = new Date()

    console.log('[Dashboard] Metrics update:', {
      updateType: updateType.value,
      metrics: metrics.value
    })
  })

  // Handle ping event (keepalive)
  sse.addEventListener('ping', createKeepaliveLogger('Dashboard'))

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
