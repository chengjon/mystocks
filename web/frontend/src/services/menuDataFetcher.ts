/**
 * Menu Data Fetcher - 菜单数据获取服务
 *
 * 负责从后端API获取菜单项的数据，集成API映射表
 *
 * @example
 * import { fetchMenuItemData } from '@/services/menuDataFetcher'
 *
 * const data = await fetchMenuItemData(menuItem)
 */

import { apiClient } from '@/api/apiClient'
import type { UnifiedResponse } from '@/api/apiClient'
import type { MenuItem } from '@/layouts/MenuConfig.enhanced'

export interface MenuDataFetchOptions {
  timeout?: number // 超时时间（毫秒）
  retries?: number // 重试次数
  cache?: boolean // 是否使用缓存
}

export interface MenuDataFetchResult<T = any> {
  success: boolean
  data?: T
  error?: string
  cached?: boolean
}

// 简单的内存缓存
const cache = new Map<string, { data: any; timestamp: number }>()
const CACHE_DURATION = 60000 // 1分钟缓存

/**
 * 从缓存获取数据
 */
const getFromCache = (key: string): any | null => {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }
  if (cached) {
    cache.delete(key) // 过期，删除
  }
  return null
}

/**
 * 保存到缓存
 */
const saveToCache = (key: string, data: any): void => {
  cache.set(key, { data, timestamp: Date.now() })
}

/**
 * 生成缓存键
 */
const generateCacheKey = (endpoint: string, method?: string): string => {
  return `${method || 'GET'}:${endpoint}`
}

/**
 * 清除缓存
 */
export const clearMenuDataCache = (pattern?: string): void => {
  if (pattern) {
    // 清除匹配pattern的缓存
    for (const key of cache.keys()) {
      if (key.includes(pattern)) {
        cache.delete(key)
      }
    }
  } else {
    // 清除所有缓存
    cache.clear()
  }
}

/**
 * 获取菜单项数据
 *
 * @param item - 菜单项配置
 * @param options - 获取选项
 * @returns Promise<MenuDataFetchResult>
 */
export async function fetchMenuItemData<T = any>(
  item: MenuItem,
  options: MenuDataFetchOptions = {}
): Promise<MenuDataFetchResult<T>> {
  const {
    timeout = 10000,
    retries = 2,
    cache: useCache = true
  } = options

  // 验证MenuItem是否配置了API端点
  if (!item.apiEndpoint) {
    return {
      success: false,
      error: `菜单项 "${item.label}" 未配置API端点`
    }
  }

  const method = item.apiMethod || 'GET'
  const cacheKey = generateCacheKey(item.apiEndpoint, method)

  // 尝试从缓存获取
  if (useCache && method === 'GET') {
    const cachedData = getFromCache(cacheKey)
    if (cachedData !== null) {
      console.log(`[MenuDataFetcher] Cache hit for: ${cacheKey}`)
      return {
        success: true,
        data: cachedData,
        cached: true
      }
    }
  }

  // 执行API请求（带重试）
  let lastError: any = null

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      console.log(`[MenuDataFetcher] Fetching: ${method} ${item.apiEndpoint} (attempt ${attempt + 1}/${retries + 1})`)

      const response = await executeWithTimeout<UnifiedResponse<T>>(
        async () => {
          switch (method.toUpperCase()) {
            case 'GET':
              return await apiClient.get<UnifiedResponse<T>>(item.apiEndpoint!)
            case 'POST':
              return await apiClient.post<UnifiedResponse<T>>(item.apiEndpoint!, {})
            case 'PUT':
              return await apiClient.put<UnifiedResponse<T>>(item.apiEndpoint!, {})
            case 'DELETE':
              return await apiClient.delete<UnifiedResponse<T>>(item.apiEndpoint!)
            default:
              throw new Error(`不支持的HTTP方法: ${method}`)
          }
        },
        timeout
      )

      // 检查响应
      if (response && response.success) {
        const data = response.data

        // 保存到缓存（仅GET请求）
        if (useCache && method === 'GET' && data !== undefined) {
          saveToCache(cacheKey, data)
        }

        console.log(`[MenuDataFetcher] Success: ${method} ${item.apiEndpoint}`)

        return {
          success: true,
          data,
          cached: false
        }
      } else {
        throw new Error(response?.message || '请求失败')
      }
    } catch (error: any) {
      lastError = error
      console.warn(`[MenuDataFetcher] Attempt ${attempt + 1} failed:`, error.message)

      // 最后一次重试失败，不再继续
      if (attempt === retries) {
        break
      }

      // 指数退避延迟
      const delay = Math.min(1000 * Math.pow(2, attempt), 5000)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  // 所有重试都失败
  const errorMessage = lastError?.message || `获取数据失败: ${item.label}`

  console.error(`[MenuDataFetcher] All retries failed: ${method} ${item.apiEndpoint}`, lastError)

  return {
    success: false,
    error: errorMessage
  }
}

/**
 * 带超时执行的Promise包装器
 */
async function executeWithTimeout<T>(
  fn: () => Promise<T>,
  timeout: number
): Promise<T> {
  return Promise.race([
    fn(),
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error(`请求超时 (${timeout}ms)`)), timeout)
    )
  ])
}

/**
 * 批量获取多个菜单项的数据
 *
 * @param items - 菜单项数组
 * @param options - 获取选项
 * @returns Promise<Map<string, MenuDataFetchResult>>
 */
export async function fetchMultipleMenuItems(
  items: MenuItem[],
  options: MenuDataFetchOptions = {}
): Promise<Map<string, MenuDataFetchResult>> {
  const results = new Map<string, MenuDataFetchResult>()

  // 并行获取所有菜单数据
  await Promise.all(
    items.map(async (item) => {
      const result = await fetchMenuItemData(item, options)
      results.set(item.path, result)
    })
  )

  return results
}

/**
 * 清除过期的缓存（定时任务）
 */
setInterval(() => {
  const now = Date.now()
  for (const [key, value] of cache.entries()) {
    if (now - value.timestamp > CACHE_DURATION) {
      cache.delete(key)
      console.log(`[MenuDataFetcher] Expired cache removed: ${key}`)
    }
  }
}, 60000) // 每分钟清理一次
