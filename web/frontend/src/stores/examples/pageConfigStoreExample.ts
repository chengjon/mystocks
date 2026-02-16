// stores/examples/pageConfigStoreExample.ts
// Store使用统一配置的示例

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getPageConfig, isRouteName, isStandardConfig } from '@/config/pageConfig'
import type { PageConfig } from '@/config/pageConfig'
import axios from 'axios'

// 路由名称类型
type RouteName = string

/**
 * PageConfig Store 示例
 * 展示如何在Store中使用统一配置
 */
export const usePageConfigExampleStore = defineStore('pageConfigExample', () => {
  // ========== 状态 ==========
  const data = ref<unknown>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentRoute = ref<RouteName | null>(null)

  // ========== 计算属性 ==========

  /**
   * 当前路由的配置
   */
  const currentPageConfig = computed(() => {
    if (!currentRoute.value) return null
    return getPageConfig(currentRoute.value)
  })

  /**
   * 是否需要实时更新
   * 注意：PageConfig 没有 realtime 属性，这里返回 false
   */
  const needsRealtimeUpdate = computed(() => {
    return false // PageConfig 类型中没有 realtime 属性
  })

  /**
   * 是否需要WebSocket连接
   * 只有 StandardPageConfig 有 wsChannel
   */
  const needsWebSocket = computed(() => {
    const config = currentPageConfig.value
    return !!(config && isStandardConfig(config) && config.wsChannel)
  })

  /**
   * WebSocket频道名称
   * 只有 StandardPageConfig 有 wsChannel
   */
  const wsChannel = computed(() => {
    const config = currentPageConfig.value
    if (config && isStandardConfig(config)) {
      return config.wsChannel ?? null
    }
    return null
  })

  // ========== 方法 ==========

  /**
   * 设置当前路由
   * @param routeName 路由名称
   */
  const setRoute = (routeName: string) => {
    // ✅ 类型安全的路由验证
    if (!isRouteName(routeName)) {
      console.warn(`⚠️ 未配置的路由: ${routeName}`)
      error.value = `未配置的路由: ${routeName}`
      return false
    }

    currentRoute.value = routeName as RouteName
    console.log(`✅ 路由已设置: ${routeName}`)
    return true
  }

  /**
   * 加载当前路由的数据
   * 使用统一配置的API端点
   */
  const loadData = async () => {
    const config = currentPageConfig.value

    if (!config) {
      error.value = '未设置有效路由'
      console.warn('⚠️ 未设置有效路由')
      return
    }

    // 只有 StandardPageConfig 有 apiEndpoint
    if (!isStandardConfig(config)) {
      error.value = '该路由不支持直接加载数据（Monolithic 类型）'
      console.warn('⚠️ Monolithic 类型路由需要通过 tab 加载数据')
      return
    }

    loading.value = true
    error.value = null

    try {
      console.log(`📡 正在加载数据: ${config.apiEndpoint}`)

      // ✅ 使用统一配置的API端点（避免硬编码）
      const response = await axios.get(config.apiEndpoint, {
        timeout: 10000
      })

      data.value = response.data

      console.log(`✅ 数据加载成功: ${config.description}`)
      return response.data
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { message?: string } }; message?: string }
      const errorMsg = axiosErr.response?.data?.message || axiosErr.message || '加载失败'
      error.value = errorMsg
      console.error(`❌ 数据加载失败: ${config.apiEndpoint}`, err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据路由名称加载数据
   * @param routeName 路由名称
   */
  const loadDataByRoute = async (routeName: RouteName) => {
    const success = setRoute(routeName)
    if (!success) {
      throw new Error(`无效的路由: ${routeName}`)
    }
    return await loadData()
  }

  /**
   * 刷新数据（重新加载）
   */
  const refresh = async () => {
    if (!currentRoute.value) {
      console.warn('⚠️ 未设置路由，无法刷新')
      return
    }

    console.log(`🔄 刷新数据: ${currentRoute.value}`)
    return await loadData()
  }

  /**
   * 清除状态
   */
  const clear = () => {
    data.value = null
    loading.value = false
    error.value = null
    currentRoute.value = null
    console.log('🗑️ Store状态已清除')
  }

  /**
   * 获取配置信息（用于调试）
   */
  const getConfigInfo = () => {
    const config = currentPageConfig.value
    if (!config) return null

    // 根据配置类型返回不同的信息
    if (isStandardConfig(config)) {
      return {
        routeName: currentRoute.value,
        type: config.type,
        apiEndpoint: config.apiEndpoint,
        wsChannel: config.wsChannel,
        description: config.description
      }
    } else {
      // MonolithicPageConfig
      return {
        routeName: currentRoute.value,
        type: config.type,
        component: config.component,
        tabCount: config.tabs.length,
        description: config.description
      }
    }
  }

  // ========== 返回 ==========
  return {
    // 状态
    data,
    loading,
    error,
    currentRoute,

    // 计算属性
    currentPageConfig,
    needsRealtimeUpdate,
    needsWebSocket,
    wsChannel,

    // 方法
    setRoute,
    loadData,
    loadDataByRoute,
    refresh,
    clear,
    getConfigInfo
  }
})

// ========== 使用示例 ==========
/**
 * 在组件中使用Store的示例代码：
 *
 * ```vue
 * <script setup lang="ts">
 * import { usePageConfigExampleStore } from '@/stores/examples/pageConfigStoreExample'
 * import { onMounted } from 'vue'
 *
 * const store = usePageConfigExampleStore()
 *
 * onMounted(async () => {
 *   // 方式1: 先设置路由，再加载数据
 *   store.setRoute('market-overview')
 *   await store.loadData()
 *
 *   // 方式2: 直接通过路由名加载数据
 *   await store.loadDataByRoute('market-realtime')
 *
 *   // 查看配置信息
 *   console.log(store.getConfigInfo())
 *
 *   // 检查是否需要实时更新
 *   if (store.needsRealtimeUpdate) {
 *     console.log('需要实时更新')
 *   }
 *
 *   // 检查是否需要WebSocket
 *   if (store.needsWebSocket) {
 *     console.log('WebSocket频道:', store.wsChannel)
 *   }
 * })
 * </script>
 *
 * <template>
 *   <div v-if="store.loading">加载中...</div>
 *   <div v-else-if="store.error">{{ store.error }}</div>
 *   <div v-else>{{ store.data }}</div>
 * </template>
 * ```
 */
