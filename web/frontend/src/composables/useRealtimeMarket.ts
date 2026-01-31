/**
 * Real-time Market Data Composable
 *
 * 提供实时市场数据的WebSocket连接和数据管理
 * 集成ArtDeco设计令牌和状态指示器
 *
 * @version 1.0
 * @created 2026-01-20
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { wsManager } from '@/services/menuService'

// ========== 类型定义 ==========

export interface RealtimeMarketData {
  symbol: string
  name?: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: number
}

export interface WebSocketStatus {
  connected: boolean
  connecting: boolean
  error: string | null
}

export interface RealtimeMarketOptions {
  autoConnect?: boolean
  reconnectOnUnmount?: boolean
  onError?: (error: Error) => void
  onMessage?: (data: RealtimeMarketData) => void
}

// ========== WebSocket状态管理 ==========

const wsStatus = ref<WebSocketStatus>({
  connected: false,
  connecting: false,
  error: null,
})

const activeSubscriptions = ref<Set<string>>(new Set())
const marketDataCache = ref<Map<string, RealtimeMarketData>>(new Map())

// ========== 主要Composable函数 ==========

/**
 * Real-time Market Data Composable
 *
 * @param options - 配置选项
 * @returns 实时市场数据API
 */
export function useRealtimeMarket(options: RealtimeMarketOptions = {}) {
  const {
    autoConnect = true,
    reconnectOnUnmount = false,
    onError,
    onMessage,
  } = options

  // ========== 连接管理 ==========

  /**
   * 连接到WebSocket服务器
   */
  const connect = () => {
    if (wsStatus.value.connected || wsStatus.value.connecting) {
      return
    }

    wsStatus.value.connecting = true
    wsStatus.value.error = null

    try {
      wsManager.connect()

      // 监听连接状态（通过订阅一个状态频道）
      const statusHandler = (data: any) => {
        if (data.status === 'connected') {
          wsStatus.value.connected = true
          wsStatus.value.connecting = false
        }
      }

      wsManager.subscribe('ws:status', statusHandler)
    } catch (error) {
      wsStatus.value.connecting = false
      wsStatus.value.error = error instanceof Error ? error.message : 'Connection failed'

      if (onError) {
        onError(error as Error)
      }
    }
  }

  /**
   * 断开WebSocket连接
   */
  const disconnect = () => {
    wsManager.disconnect()
    wsStatus.value.connected = false
    wsStatus.value.connecting = false
    activeSubscriptions.value.clear()
  }

  // ========== 订阅管理 ==========

  /**
   * 订阅股票实时行情
   *
   * @param symbol - 股票代码
   * @param callback - 数据更新回调
   * @returns 取消订阅函数
   */
  const subscribeStock = (
    symbol: string,
    callback?: (data: RealtimeMarketData) => void
  ): (() => void) => {
    const channel = `market:realtime:${symbol}`

    // 添加到活跃订阅
    activeSubscriptions.value.add(channel)

    // 确保已连接
    if (!wsStatus.value.connected) {
      connect()
    }

    // 创建消息处理器
    const handler = (rawData: any) => {
      const data: RealtimeMarketData = {
        symbol: rawData.symbol || symbol,
        name: rawData.name,
        price: rawData.price,
        change: rawData.change,
        changePercent: rawData.changePercent,
        volume: rawData.volume,
        timestamp: rawData.timestamp || Date.now(),
      }

      // 更新缓存
      marketDataCache.value.set(symbol, data)

      // 触发回调
      if (callback) {
        callback(data)
      }

      // 触发全局回调
      if (onMessage) {
        onMessage(data)
      }

      // 触发自定义事件（用于跨组件通信）
      window.dispatchEvent(
        new CustomEvent('market-update', {
          detail: { symbol, data },
        })
      )
    }

    // 订阅频道
    wsManager.subscribe(channel, handler)

    // 返回取消订阅函数
    return () => {
      wsManager.unsubscribe(channel, handler)
      activeSubscriptions.value.delete(channel)
      marketDataCache.value.delete(symbol)
    }
  }

  /**
   * 批量订阅股票
   *
   * @param symbols - 股票代码数组
   * @param callback - 数据更新回调
   * @returns 取消订阅函数
   */
  const subscribeStocks = (
    symbols: string[],
    callback?: (data: RealtimeMarketData) => void
  ): (() => void) => {
    const unsubscribers: Array<() => void> = []

    symbols.forEach(symbol => {
      const unsubscribe = subscribeStock(symbol, callback)
      unsubscribers.push(unsubscribe)
    })

    // 返回批量取消订阅函数
    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe())
    }
  }

  /**
   * 订阅市场概览
   *
   * @param callback - 数据更新回调
   * @returns 取消订阅函数
   */
  const subscribeMarketSummary = (
    callback?: (data: any) => void
  ): (() => void) => {
    const channel = 'market:summary'

    activeSubscriptions.value.add(channel)

    if (!wsStatus.value.connected) {
      connect()
    }

    const handler = (data: any) => {
      if (callback) {
        callback(data)
      }

      // 触发自定义事件
      window.dispatchEvent(
        new CustomEvent('market-summary-update', { detail: data })
      )
    }

    wsManager.subscribe(channel, handler)

    return () => {
      wsManager.unsubscribe(channel, handler)
      activeSubscriptions.value.delete(channel)
    }
  }

  // ========== 数据获取 ==========

  /**
   * 获取股票实时数据（从缓存）
   *
   * @param symbol - 股票代码
   * @returns 实时数据或null
   */
  const getStockData = (symbol: string): RealtimeMarketData | null => {
    return marketDataCache.value.get(symbol) || null
  }

  /**
   * 获取所有订阅的股票数据
   *
   * @returns 实时数据Map
   */
  const getAllStockData = (): Map<string, RealtimeMarketData> => {
    return new Map(marketDataCache.value)
  }

  // ========== 计算属性 ==========

  /**
   * 连接状态文本（用于显示）
   */
  const statusText = computed(() => {
    if (wsStatus.value.connecting) return '连接中...'
    if (wsStatus.value.connected) return '已连接'
    if (wsStatus.value.error) return `错误: ${wsStatus.value.error}`
    return '未连接'
  })

  /**
   * 连接状态类型（用于ArtDecoStatusIndicator）
   */
  const statusType = computed<'active' | 'warning' | 'error' | 'idle'>(() => {
    if (wsStatus.value.connecting) return 'warning'
    if (wsStatus.value.connected) return 'active'
    if (wsStatus.value.error) return 'error'
    return 'idle'
  })

  /**
   * 活跃订阅数量
   */
  const subscriptionCount = computed(() => {
    return activeSubscriptions.value.size
  })

  // ========== 生命周期 ==========

  if (autoConnect) {
    onMounted(() => {
      connect()
    })
  }

  onUnmounted(() => {
    if (!reconnectOnUnmount) {
      disconnect()
    }
  })

  // ========== 返回API ==========

  return {
    // 连接管理
    connect,
    disconnect,

    // 订阅管理
    subscribeStock,
    subscribeStocks,
    subscribeMarketSummary,

    // 数据获取
    getStockData,
    getAllStockData,

    // 状态
    status: wsStatus,
    statusText,
    statusType,
    subscriptionCount,

    // 缓存
    marketDataCache,
  }
}

// ========== 全局事件监听辅助函数 ==========

/**
 * 监听市场数据更新事件
 *
 * @param callback - 事件回调
 * @returns 清理函数
 */
export function onMarketUpdate(
  callback: (symbol: string, data: RealtimeMarketData) => void
): () => void {
  const handler = (event: Event) => {
    const customEvent = event as CustomEvent<{ symbol: string; data: RealtimeMarketData }>
    callback(customEvent.detail.symbol, customEvent.detail.data)
  }

  window.addEventListener('market-update', handler as EventListener)

  return () => {
    window.removeEventListener('market-update', handler as EventListener)
  }
}

/**
 * 监听市场概览更新事件
 *
 * @param callback - 事件回调
 * @returns 清理函数
 */
export function onMarketSummaryUpdate(
  callback: (data: any) => void
): () => void {
  const handler = (event: Event) => {
    const customEvent = event as CustomEvent<any>
    callback(customEvent.detail)
  }

  window.addEventListener('market-summary-update', handler as EventListener)

  return () => {
    window.removeEventListener('market-summary-update', handler as EventListener)
  }
}

// ========== 默认导出 ==========

export default useRealtimeMarket
