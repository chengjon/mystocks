/**
 * Menu Data Fetcher Unit Tests
 *
 * 测试菜单数据获取服务的核心功能
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fetchMenuItemData, fetchMultipleMenuItems, clearMenuDataCache } from '../menuDataFetcher'
import type { MenuItem } from '@/layouts/MenuConfig'

// Mock apiClient
vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

import { apiClient } from '@/api/apiClient'

describe('menuDataFetcher', () => {
  const mockMenuItem: MenuItem = {
    path: '/test',
    label: '测试菜单',
    icon: 'test',
    apiEndpoint: '/api/test',
    apiMethod: 'GET'
  }

  beforeEach(() => {
    // 清除所有缓存
    clearMenuDataCache()

    // 重置所有mock
    vi.clearAllMocks()
  })

  describe('基础功能', () => {
    it('应该成功获取GET请求数据', async () => {
      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { result: 'test data' },
        timestamp: new Date().toISOString(),
        request_id: 'req-1',
        errors: null
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await fetchMenuItemData(mockMenuItem)

      expect(result.success).toBe(true)
      expect(result.data).toEqual({ result: 'test data' })
      expect(result.cached).toBe(false)
      expect(apiClient.get).toHaveBeenCalledWith('/api/test')
    })

    it('应该成功获取POST请求数据', async () => {
      const postMenuItem: MenuItem = {
        ...mockMenuItem,
        apiMethod: 'POST'
      }

      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { created: true },
        timestamp: new Date().toISOString(),
        request_id: 'req-2',
        errors: null
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await fetchMenuItemData(postMenuItem)

      expect(result.success).toBe(true)
      expect(result.data).toEqual({ created: true })
      expect(apiClient.post).toHaveBeenCalledWith('/api/test', {})
    })

    it('应该成功获取PUT请求数据', async () => {
      const putMenuItem: MenuItem = {
        ...mockMenuItem,
        apiMethod: 'PUT'
      }

      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { updated: true },
        timestamp: new Date().toISOString(),
        request_id: 'req-3',
        errors: null
      }

      vi.mocked(apiClient.put).mockResolvedValue(mockResponse)

      const result = await fetchMenuItemData(putMenuItem)

      expect(result.success).toBe(true)
      expect(result.data).toEqual({ updated: true })
      expect(apiClient.put).toHaveBeenCalledWith('/api/test', {})
    })

    it('应该成功获取DELETE请求数据', async () => {
      const deleteMenuItem: MenuItem = {
        ...mockMenuItem,
        apiMethod: 'DELETE'
      }

      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { deleted: true },
        timestamp: new Date().toISOString(),
        request_id: 'req-4',
        errors: null
      }

      vi.mocked(apiClient.delete).mockResolvedValue(mockResponse)

      const result = await fetchMenuItemData(deleteMenuItem)

      expect(result.success).toBe(true)
      expect(result.data).toEqual({ deleted: true })
      expect(apiClient.delete).toHaveBeenCalledWith('/api/test')
    })
  })

  describe('错误处理', () => {
    it('应该处理缺失apiEndpoint的菜单项', async () => {
      const invalidMenuItem: MenuItem = {
        path: '/test',
        label: '测试',
        icon: 'test'
        // 缺少apiEndpoint
      }

      const result = await fetchMenuItemData(invalidMenuItem)

      expect(result.success).toBe(false)
      expect(result.error).toContain('未配置API端点')
    })

    it('应该处理API错误响应', async () => {
      const mockResponse = {
        success: false,
        code: 500,
        message: 'Internal Server Error',
        data: null,
        timestamp: new Date().toISOString(),
        request_id: 'req-5',
        errors: null
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await fetchMenuItemData(mockMenuItem)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Internal Server Error')
    })

    it('应该处理网络错误', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network Error'))

      const result = await fetchMenuItemData(mockMenuItem)

      expect(result.success).toBe(false)
      expect(result.error).toContain('获取数据失败')
    })

    it('应该处理超时错误', async () => {
      // 模拟超时
      vi.mocked(apiClient.get).mockImplementation(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), 2000)
        )
      )

      const result = await fetchMenuItemData(mockMenuItem, { timeout: 100 })

      expect(result.success).toBe(false)
      expect(result.error).toContain('超时')
    })
  })

  describe('缓存功能', () => {
    it('应该缓存GET请求结果', async () => {
      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { value: 1 },
        timestamp: new Date().toISOString(),
        request_id: 'req-6',
        errors: null
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      // 第一次请求
      const result1 = await fetchMenuItemData(mockMenuItem, { cache: true })
      expect(result1.cached).toBe(false)
      expect(apiClient.get).toHaveBeenCalledTimes(1)

      // 第二次请求（应该从缓存获取）
      const result2 = await fetchMenuItemData(mockMenuItem, { cache: true })
      expect(result2.cached).toBe(true)
      expect(apiClient.get).toHaveBeenCalledTimes(1) // 没有额外调用
    })

    it('不应该缓存POST请求结果', async () => {
      const postMenuItem: MenuItem = {
        ...mockMenuItem,
        apiMethod: 'POST'
      }

      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { created: true },
        timestamp: new Date().toISOString(),
        request_id: 'req-7',
        errors: null
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      // 第一次请求
      const result1 = await fetchMenuItemData(postMenuItem, { cache: true })
      expect(result1.cached).toBe(false)
      expect(apiClient.post).toHaveBeenCalledTimes(1)

      // 第二次请求（POST不应该缓存）
      const result2 = await fetchMenuItemData(postMenuItem, { cache: true })
      expect(result2.cached).toBe(false)
      expect(apiClient.post).toHaveBeenCalledTimes(2) // 应该再次调用
    })

    it('应该支持清除缓存', async () => {
      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { value: 1 },
        timestamp: new Date().toISOString(),
        request_id: 'req-8',
        errors: null
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      // 第一次请求
      await fetchMenuItemData(mockMenuItem, { cache: true })

      // 清除缓存
      clearMenuDataCache(mockMenuItem.apiEndpoint)

      // 第二次请求（缓存已清除，应该重新请求）
      const result2 = await fetchMenuItemData(mockMenuItem, { cache: true })
      expect(result2.cached).toBe(false)
      expect(apiClient.get).toHaveBeenCalledTimes(2)
    })

    it('应该支持清除所有缓存', async () => {
      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { value: 1 },
        timestamp: new Date().toISOString(),
        request_id: 'req-9',
        errors: null
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      // 第一次请求
      await fetchMenuItemData(mockMenuItem, { cache: true })

      // 清除所有缓存
      clearMenuDataCache()

      // 第二次请求（缓存已清除）
      const result2 = await fetchMenuItemData(mockMenuItem, { cache: true })
      expect(result2.cached).toBe(false)
      expect(apiClient.get).toHaveBeenCalledTimes(2)
    })

    it('应该支持模式匹配清除缓存', async () => {
      const menuItem1: MenuItem = {
        ...mockMenuItem,
        apiEndpoint: '/api/market/realtime'
      }

      const menuItem2: MenuItem = {
        ...mockMenuItem,
        path: '/test2',
        apiEndpoint: '/api/market/summary'
      }

      const mockResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: { value: 1 },
        timestamp: new Date().toISOString(),
        request_id: 'req-10',
        errors: null
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      // 缓存两个请求
      await fetchMenuItemData(menuItem1, { cache: true })
      await fetchMenuItemData(menuItem2, { cache: true })

      // 使用模式清除缓存
      clearMenuDataCache('/api/market')

      // 两个缓存都应该被清除
      const result1 = await fetchMenuItemData(menuItem1, { cache: true })
      const result2 = await fetchMenuItemData(menuItem2, { cache: true })

      expect(result1.cached).toBe(false)
      expect(result2.cached).toBe(false)
    })
  })

  describe('重试机制', () => {
    it('应该在失败时重试', async () => {
      let attempts = 0
      vi.mocked(apiClient.get).mockImplementation(() => {
        attempts++
        if (attempts < 3) {
          return Promise.reject(new Error('Temporary Error'))
        }
        return Promise.resolve({
          success: true,
          code: 200,
          message: 'OK',
          data: { value: 1 },
          timestamp: new Date().toISOString(),
          request_id: 'req-11',
          errors: null
        })
      })

      const result = await fetchMenuItemData(mockMenuItem, { retries: 3 })

      expect(result.success).toBe(true)
      expect(attempts).toBe(3)
    })

    it('应该在所有重试失败后返回错误', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Persistent Error'))

      const result = await fetchMenuItemData(mockMenuItem, { retries: 2 })

      expect(result.success).toBe(false)
      expect(result.error).toContain('获取数据失败')
      expect(apiClient.get).toHaveBeenCalledTimes(3) // 初始调用 + 2次重试
    })

    it('应该使用指数退避延迟', async () => {
      const timestamps: number[] = []
      vi.mocked(apiClient.get).mockImplementation(() => {
        timestamps.push(Date.now())
        return Promise.reject(new Error('Error'))
      })

      const startTime = Date.now()
      await fetchMenuItemData(mockMenuItem, { retries: 2 })
      const endTime = Date.now()

      // 验证有延迟（应该大于1000ms，因为有指数退避）
      expect(endTime - startTime).toBeGreaterThan(500)
    })
  })

  describe('批量获取', () => {
    it('应该并行获取多个菜单项数据', async () => {
      const menuItems: MenuItem[] = [
        { ...mockMenuItem, path: '/test1', apiEndpoint: '/api/test1' },
        { ...mockMenuItem, path: '/test2', apiEndpoint: '/api/test2' },
        { ...mockMenuItem, path: '/test3', apiEndpoint: '/api/test3' }
      ]

      menuItems.forEach((item, index) => {
        vi.mocked(apiClient.get).mockResolvedValue({
          success: true,
          code: 200,
          message: 'OK',
          data: { index },
          timestamp: new Date().toISOString(),
          request_id: `req-${index}`,
          errors: null
        })
      })

      const results = await fetchMultipleMenuItems(menuItems)

      expect(results.size).toBe(3)

      menuItems.forEach((item, index) => {
        const result = results.get(item.path)
        expect(result?.success).toBe(true)
        expect(result?.data).toEqual({ index })
      })
    })

    it('应该处理批量获取中的部分失败', async () => {
      const menuItems: MenuItem[] = [
        { ...mockMenuItem, path: '/test1', apiEndpoint: '/api/test1' },
        { ...mockMenuItem, path: '/test2', apiEndpoint: '/api/test2' },
        { ...mockMenuItem, path: '/test3', apiEndpoint: '/api/test3' }
      ]

      // 第二个请求失败
      vi.mocked(apiClient.get).mockImplementation((url: string) => {
        if (url === '/api/test2') {
          return Promise.reject(new Error('API Error'))
        }
        return Promise.resolve({
          success: true,
          code: 200,
          message: 'OK',
          data: { ok: true },
          timestamp: new Date().toISOString(),
          request_id: 'req-ok',
          errors: null
        })
      })

      const results = await fetchMultipleMenuItems(menuItems)

      expect(results.size).toBe(3)

      expect(results.get('/test1')?.success).toBe(true)
      expect(results.get('/test2')?.success).toBe(false)
      expect(results.get('/test3')?.success).toBe(true)
    })
  })

  describe('不支持的HTTP方法', () => {
    it('应该抛出不支持的方法错误', async () => {
      const invalidMenuItem: MenuItem = {
        ...mockMenuItem,
        apiMethod: 'PATCH' as any
      }

      const result = await fetchMenuItemData(invalidMenuItem)

      expect(result.success).toBe(false)
      expect(result.error).toContain('不支持的HTTP方法')
    })
  })
})
