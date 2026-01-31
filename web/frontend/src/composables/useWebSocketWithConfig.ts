/**
 * useWebSocketWithConfig - 基于统一配置的WebSocket Composable
 *
 * Phase 3: WebSocket解耦版本
 *
 * 核心特性：
 * - 基于路由自动订阅（从统一配置读取频道）
 * - 无硬编码频道名
 * - 类型安全的路由管理
 * - 复用 useWebSocketEnhanced 的底层功能
 *
 * @example
 * // 基础用法：根据路由名订阅
 * const { subscribeByRoute, unsubscribeByRoute } = useWebSocketWithConfig()
 * subscribeByRoute('market-realtime', (data) => console.log(data))
 *
 * @example
 * // 批量订阅所有WebSocket路由
 * const { subscribeAllWebSocketRoutes } = useWebSocketWithConfig()
 * subscribeAllWebSocketRoutes((data) => console.log(data))
 *
 * @see docs/architecture/FRONTEND_OPTIMIZATION_IMPLEMENTATION_PLAN_V2.md Phase 3
 */

import { computed } from 'vue'
import { useWebSocket } from './useWebSocketEnhanced'
import {
  PAGE_CONFIG,
  getPageConfig,
  isRouteName
  getWebSocketRoutes,
  type RouteName
} from '@/config/pageConfig'

// 消息回调类型
type MessageCallback = (data: any) => void

/**
 * 基于统一配置的WebSocket Composable
 *
 * 解耦WebSocket与路由的耦合，基于PAGE_CONFIG自动管理频道订阅
 */
export function useWebSocketWithConfig() {
  // 使用增强版WebSocket的底层功能
  const {
    connectionState,
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
    subscribe,        // 订阅频道（频道名，回调）
    unsubscribe,      // 取消订阅频道
    send,
    getActiveSubscriptions,
    getSubscriberCount
  } = useWebSocket()

  /**
   * 根据路由名订阅频道（从统一配置读取）
   *
   * @param routeName 路由名称（类型安全）
   * @param callback 消息回调函数
   * @returns 取消订阅函数
   *
   * @example
   * const unsubscribe = subscribeByRoute('market-realtime', (data) => {
   *   console.log('收到市场实时数据:', data)
   * })
   */
  const subscribeByRoute = (routeName: RouteName, callback: MessageCallback) => {
    // ✅ 类型安全的路由验证
    if (!isValidRouteName(routeName)) {
      console.error(`[WebSocket] 无效的路由名: ${routeName}`)
      return () => {} // 返回空函数
    }

    const config = PAGE_CONFIG[routeName]

    // ✅ 从统一配置读取频道（无硬编码）
    if (!config.wsChannel) {
      console.warn(`[WebSocket] 路由 ${routeName} 不需要WebSocket连接`)
      return () => {} // 返回空函数
    }

    const channel = config.wsChannel

    console.log(`[WebSocket] 订阅路由 ${routeName} 的频道: ${channel}`)

    // 调用底层subscribe函数
    return subscribe(channel, callback)
  }

  /**
   * 根据路由名取消订阅频道
   *
   * @param routeName 路由名称
   * @param callback 消息回调函数
   *
   * @example
   * unsubscribeByRoute('market-realtime', callback)
   */
  const unsubscribeByRoute = (routeName: RouteName, callback: MessageCallback) => {
    // ✅ 类型安全的路由验证
    if (!isValidRouteName(routeName)) {
      console.error(`[WebSocket] 无效的路由名: ${routeName}`)
      return
    }

    const config = PAGE_CONFIG[routeName]

    // ✅ 从统一配置读取频道
    if (!config.wsChannel) {
      console.warn(`[WebSocket] 路由 ${routeName} 不需要WebSocket连接`)
      return
    }

    const channel = config.wsChannel

    console.log(`[WebSocket] 取消订阅路由 ${routeName} 的频道: ${channel}`)

    // 调用底层unsubscribe函数
    unsubscribe(channel, callback)
  }

  /**
   * 订阅所有需要WebSocket的路由
   *
   * @param callback 统一的消息回调函数
   * @returns 取消所有订阅的函数
   *
   * @example
   * const unsubscribeAll = subscribeAllWebSocketRoutes((data) => {
   *   console.log('收到WebSocket消息:', data)
   * })
   *
   * // 稍后取消所有订阅
   * unsubscribeAll()
   */
  const subscribeAllWebSocketRoutes = (callback: MessageCallback) => {
    // ✅ 从统一配置获取所有需要WebSocket的路由
    const wsRoutes = getWebSocketRoutes()

    console.log(`[WebSocket] 批量订阅 ${wsRoutes.length} 个路由的WebSocket频道`)

    const unsubscribers: Array<() => void> = []

    // 为每个路由订阅
    wsRoutes.forEach(({ routeName, channel }) => {
      console.log(`[WebSocket] 订阅 ${routeName} -> ${channel}`)
      const unsubscribe = subscribe(channel, callback)
      unsubscribers.push(unsubscribe)
    })

    // 返回取消所有订阅的函数
    return () => {
      console.log(`[WebSocket] 取消所有 ${unsubscribers.length} 个订阅`)
      unsubscribers.forEach(unsub => unsub())
    }
  }

  /**
   * 根据当前路由自动订阅
   *
   * @param currentRouteName 当前路由名
   * @param callback 消息回调函数
   * @returns 取消订阅函数
   *
   * @example
   * const route = useRoute()
   * const { autoSubscribeByCurrentRoute } = useWebSocketWithConfig()
   *
   * const unsubscribe = autoSubscribeByCurrentRoute(
   *   route.name as string,
   *   (data) => console.log(data)
   * )
   */
  const autoSubscribeByCurrentRoute = (
    currentRouteName: string,
    callback: MessageCallback
  ) => {
    // ✅ 验证路由名
    if (!isValidRouteName(currentRouteName)) {
      console.warn(`[WebSocket] 未配置的路由: ${currentRouteName}`)
      return () => {}
    }

    const routeName = currentRouteName as RouteName
    const config = PAGE_CONFIG[routeName]

    // ✅ 检查是否需要WebSocket
    if (!config.wsChannel) {
      console.log(`[WebSocket] 路由 ${routeName} 不需要WebSocket`)
      return () => {}
    }

    // ✅ 自动订阅
    return subscribeByRoute(routeName, callback)
  }

  /**
   * 获取路由的WebSocket频道信息
   *
   * @param routeName 路由名称
   * @returns 频道信息或null
   *
   * @example
   * const channelInfo = getRouteChannelInfo('market-realtime')
   * console.log(channelInfo)
   * // { routeName: 'market-realtime', channel: 'market:realtime' }
   */
  const getRouteChannelInfo = (routeName: RouteName) => {
    const config = getPageConfig(routeName)

    if (!config || !config.wsChannel) {
      return null
    }

    return {
      routeName,
      channel: config.wsChannel,
      description: config.description
    }
  }

  /**
   * 获取所有WebSocket频道信息
   *
   * @returns 频道信息数组
   *
   * @example
   * const allChannels = getAllWebSocketChannels()
   * console.log(allChannels)
   * // [
   * //   { routeName: 'market-realtime', channel: 'market:realtime', description: '...' },
   * //   { routeName: 'trading-signals', channel: 'trading:signals', description: '...' },
   * //   ...
   * // ]
   */
  const getAllWebSocketChannels = () => {
    return getWebSocketRoutes().map(({ routeName, channel }) => ({
      routeName,
      channel,
      description: PAGE_CONFIG[routeName].description
    }))
  }

  /**
   * 检查路由是否需要WebSocket连接
   *
   * @param routeName 路由名称
   * @returns 是否需要WebSocket
   *
   * @example
   * if (routeNeedsWebSocket('market-realtime')) {
   *   console.log('需要WebSocket连接')
   * }
   */
  const routeNeedsWebSocket = (routeName: RouteName): boolean => {
    const config = getPageConfig(routeName)
    return !!config?.wsChannel
  }

  /**
   * 计算属性：当前已订阅的路由列表
   */
  const subscribedRoutes = computed(() => {
    const activeChannels = getActiveSubscriptions()

    // 反向查找：频道名 -> 路由名
    return getWebSocketRoutes()
      .filter(({ channel }) => activeChannels.includes(channel))
      .map(({ routeName }) => routeName)
  })

  /**
   * 计算属性：订阅统计
   */
  const subscriptionStats = computed(() => {
    const allWsRoutes = getWebSocketRoutes()
    const activeChannels = getActiveSubscriptions()

    return {
      total: allWsRoutes.length,
      subscribed: subscribedRoutes.value.length,
      channels: activeChannels.length
    }
  })

  return {
    // ========== 状态 ==========
    connectionState,
    isConnected,
    lastMessage,
    error,
    subscribedRoutes,
    subscriptionStats,

    // ========== 基础方法（来自useWebSocketEnhanced） ==========
    connect,
    disconnect,
    send,
    getActiveSubscriptions,
    getSubscriberCount,

    // ========== 统一配置方法（Phase 3新增） ==========
    subscribeByRoute,
    unsubscribeByRoute,
    subscribeAllWebSocketRoutes,
    autoSubscribeByCurrentRoute,
    getRouteChannelInfo,
    getAllWebSocketChannels,
    routeNeedsWebSocket
  }
}

/**
 * 使用示例：
 *
 * ```vue
 * <script setup lang="ts">
 * import { useWebSocketWithConfig } from '@/composables/useWebSocketWithConfig'
 * import { useRoute } from 'vue-router'
 * import { onMounted, onUnmounted } from 'vue'
 *
 * const route = useRoute()
 * const { autoSubscribeByCurrentRoute } = useWebSocketWithConfig()
 *
 * const handleMessage = (data: any) => {
 *   console.log('收到WebSocket消息:', data)
 * }
 *
 * let unsubscribe: (() => void) | null = null
 *
 * onMounted(() => {
 *   // ✅ 根据当前路由自动订阅（无硬编码）
 *   unsubscribe = autoSubscribeByCurrentRoute(route.name as string, handleMessage)
 * })
 *
 * onUnmounted(() => {
 *   // ✅ 清理订阅
 *   unsubscribe?.()
 * })
 * </script>
 * ```
 */
