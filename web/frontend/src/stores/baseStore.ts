// stores/baseStore.ts - 统一Store模板
import { defineStore } from 'pinia'
import { _ref, reactive, computed } from 'vue'

export interface BaseStoreState {
  data: unknown | null
  loading: boolean
  error: string | null
  lastFetch: number | null
  cacheValid: boolean
}

export function createBaseStore(
  storeId: string,
  initialData: unknown | null = null
) {
  return defineStore(storeId, () => {
    const state = reactive<BaseStoreState>({
      data: initialData,
      loading: false,
      error: null,
      lastFetch: null,
      cacheValid: false
    })

    const isStale = computed(() => {
      if (!state.lastFetch) return true
      const age = Date.now() - state.lastFetch
      return age > 5 * 60 * 1000 // 5分钟过期
    })

    const canUseCache = computed(() => {
      return state.data !== null && !state.loading && !isStale.value
    })

    const executeApiCall = async <R>(
      operation: () => Promise<R>,
      options: {
        cacheKey?: string
        skipCache?: boolean
        forceRefresh?: boolean
        errorContext?: string
      } = {}
    ): Promise<R> => {
      const { skipCache = false, forceRefresh = false, errorContext = storeId } = options

      if (!skipCache && !forceRefresh && canUseCache.value) {
        console.log(`📦 使用缓存数据: ${storeId}`)
        return state.data as R
      }

      state.loading = true
      state.error = null

      try {
        const result = await operation()

        state.data = result
        state.lastFetch = Date.now()
        state.cacheValid = true
        state.loading = false

        console.log(`✅ API调用成功: ${storeId}`)
        return result

      } catch (error) {
        state.loading = false

        const errorMessage = handleApiError(error, errorContext)
        state.error = errorMessage

        console.error(`❌ API调用失败: ${storeId}`, error)
        throw error
      }
    }

    const refresh = async () => {
      throw new Error('refresh method must be implemented by subclass')
    }

    const clear = () => {
      state.data = initialData
      state.loading = false
      state.error = null
      state.lastFetch = null
      state.cacheValid = false
    }

    return {
      state: readonly(state),
      isStale,
      canUseCache,
      executeApiCall,
      refresh,
      clear
    }
  })
}

function handleApiError(error: unknown, context: string): string {
  console.error(`API Error in ${context}:`, error)

  if (error.response) {
    const status = error.response.status
    switch (status) {
      case 401:
        return '登录已过期，请重新登录'
      case 403:
        return '权限不足'
      case 404:
        return '请求的资源不存在'
      case 429:
        return '请求过于频繁，请稍后再试'
      case 500:
        return '服务器内部错误'
      default:
        return error.response.data?.message || '请求失败'
    }
  } else if (error.request) {
    return '网络连接失败，请检查网络连接'
  } else {
    return '请求配置错误'
  }
}
