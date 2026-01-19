/**
 * useWebSocket - 增强版WebSocket Composable
 *
 * 功能：
 * - WebSocket连接管理
 * - 频道订阅/取消订阅
 * - 自动重连机制
 * - 心跳保活
 * - 消息回调系统
 * - 连接状态管理
 *
 * @example
 * const { connect, disconnect, subscribe, unsubscribe } = useWebSocket()
 * connect('ws://localhost:8000/api/ws')
 * subscribe('market:realtime', (data) => console.log(data))
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

// WebSocket连接状态
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error'

// 消息回调类型
type MessageCallback = (data: any) => void

interface WebSocketConfig {
  url?: string
  reconnectInterval?: number  // 重连间隔（毫秒）
  maxReconnectAttempts?: number  // 最大重连次数
  heartbeatInterval?: number  // 心跳间隔（毫秒）
}

interface WebSocketState {
  ws: WebSocket | null
  connectionState: ConnectionState
  reconnectAttempts: number
  reconnectTimer: number | null
  heartbeatTimer: number | null
  subscriptions: Map<string, Set<MessageCallback>>
  lastMessage: any
  error: Event | null
}

// 全局WebSocket状态（单例模式）
const globalState = ref<WebSocketState>({
  ws: null,
  connectionState: 'disconnected',
  reconnectAttempts: 0,
  reconnectTimer: null,
  heartbeatTimer: null,
  subscriptions: new Map(),
  lastMessage: null,
  error: null
})

export function useWebSocket(config: WebSocketConfig = {}) {
  // 合并配置
  const {
    url = 'ws://localhost:8000/api/ws',
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    heartbeatInterval = 30000
  } = config

  const connectionState = computed<ConnectionState>(() => globalState.value.connectionState)
  const isConnected = computed(() => globalState.value.connectionState === 'connected')
  const lastMessage = computed(() => globalState.value.lastMessage)
  const error = computed(() => globalState.value.error)

  /**
   * 连接WebSocket
   */
  const connect = () => {
    if (globalState.value.ws?.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Already connected')
      return
    }

    globalState.value.connectionState = 'connecting'

    try {
      globalState.value.ws = new WebSocket(url)

      globalState.value.ws.onopen = () => {
        console.log('[WebSocket] Connected to', url)
        globalState.value.connectionState = 'connected'
        globalState.value.reconnectAttempts = 0

        // 启动心跳
        startHeartbeat()

        // 触发连接成功回调
        if (connectionState.value !== 'connected') {
          // 可以在这里触发全局事件
        }
      }

      globalState.value.ws.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          globalState.value.lastMessage = data

          // 处理频道消息
          if (data.channel && data.payload) {
            const callbacks = globalState.value.subscriptions.get(data.channel)
            if (callbacks) {
              callbacks.forEach(callback => {
                try {
                  callback(data.payload)
                } catch (error) {
                  console.error('[WebSocket] Callback error:', error)
                }
              })
            }
          }

          // 处理系统消息
          if (data.type === 'pong') {
            // 心跳响应
          }
        } catch (e) {
          console.error('[WebSocket] Message parse error:', e)
          globalState.value.lastMessage = event.data
        }
      }

      globalState.value.ws.onerror = (event: Event) => {
        console.error('[WebSocket] Error:', event)
        globalState.value.connectionState = 'error'
        globalState.value.error = event

        // 尝试重连
        scheduleReconnect()
      }

      globalState.ws.onclose = () => {
        console.log('[WebSocket] Disconnected')
        globalState.value.connectionState = 'disconnected'
        globalState.value.ws = null

        // 尝试重连
        scheduleReconnect()
      }
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error)
      globalState.value.connectionState = 'error'
      scheduleReconnect()
    }
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    stopHeartbeat()
    clearReconnectTimer()

    if (globalState.value.ws) {
      globalState.value.ws.close()
      globalState.value.ws = null
    }

    globalState.value.connectionState = 'disconnected'
  }

  /**
   * 订划重连
   */
  const scheduleReconnect = () => {
    if (globalState.value.reconnectAttempts >= maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached')
      return
    }

    if (globalState.value.reconnectTimer) {
      return // 已经有重连定时器
    }

    globalState.value.reconnectAttempts++
    const delay = reconnectInterval * globalState.value.reconnectAttempts

    console.log(`[WebSocket] Scheduling reconnect in ${delay}ms (attempt ${globalState.value.reconnectAttempts}/${maxReconnectAttempts})`)

    globalState.value.reconnectTimer = window.setTimeout(() => {
      globalState.value.reconnectTimer = null
      connect()
    }, delay)
  }

  /**
   * 清除重连定时器
   */
  const clearReconnectTimer = () => {
    if (globalState.value.reconnectTimer) {
      clearTimeout(globalState.value.reconnectTimer)
      globalState.value.reconnectTimer = null
    }
  }

  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    if (globalState.value.heartbeatTimer) {
      return // 已经有心跳定时器
    }

    globalState.value.heartbeatTimer = window.setInterval(() => {
      if (globalState.value.ws?.readyState === WebSocket.OPEN) {
        globalState.value.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (globalState.value.heartbeatTimer) {
      clearInterval(globalState.value.heartbeatTimer)
      globalState.value.heartbeatTimer = null
    }
  }

  /**
   * 订阅频道
   */
  const subscribe = (channel: string, callback: MessageCallback) => () => {
    if (!globalState.value.subscriptions.has(channel)) {
      globalState.value.subscriptions.set(channel, new Set())
    }

    globalState.value.subscriptions.get(channel)!.add(callback)

    // 发送订阅消息
    if (globalState.value.ws?.readyState === WebSocket.OPEN) {
      globalState.value.ws.send(JSON.stringify({
        type: 'subscribe',
        channel: channel
      }))
    }

    console.log(`[WebSocket] Subscribed to channel: ${channel}`)

    // 返回取消订阅函数
    return () => unsubscribe(channel, callback)
  }

  /**
   * 取消订阅频道
   */
  const unsubscribe = (channel: string, callback: MessageCallback) => {
    const callbacks = globalState.value.subscriptions.get(channel)
    if (callbacks) {
      callbacks.delete(callback)

      // 如果该频道没有订阅者了，发送取消订阅消息
      if (callbacks.size === 0) {
        globalState.value.subscriptions.delete(channel)

        if (globalState.value.ws?.readyState === WebSocket.OPEN) {
          globalState.value.ws.send(JSON.stringify({
            type: 'unsubscribe',
            channel: channel
          }))
        }

        console.log(`[WebSocket] Unsubscribed from channel: ${channel}`)
      }
    }
  }

  /**
   * 发送消息
   */
  const send = (data: any) => {
    if (globalState.value.ws?.readyState === WebSocket.OPEN) {
      globalState.value.ws.send(JSON.stringify(data))
    } else {
      console.warn('[WebSocket] Cannot send message: not connected')
    }
  }

  /**
   * 获取活跃订阅列表
   */
  const getActiveSubscriptions = () => {
    return Array.from(globalState.value.subscriptions.keys())
  }

  /**
   * 获取指定频道的订阅者数量
   */
  const getSubscriberCount = (channel: string) => {
    return globalState.value.subscriptions.get(channel)?.size || 0
  }

  // 组件挂载时自动连接
  onMounted(() => {
    connect()
  })

  // 组件卸载时断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    // 状态
    connectionState,
    isConnected,
    lastMessage,
    error,

    // 方法
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    send,
    getActiveSubscriptions,
    getSubscriberCount
  }
}
