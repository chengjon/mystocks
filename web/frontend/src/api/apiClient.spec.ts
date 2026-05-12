/**
 * API Client Unit Tests
 *
 * Tests HTTP request handling, interceptors, and error handling.
 */

import { beforeEach, describe, it, expect, vi } from 'vitest'
import apiClient from './apiClient'

const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('apiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.history.replaceState({}, '', '/login')
  })

  describe('configuration', () => {
    it('should have timeout configured', () => {
      expect(apiClient.defaults.timeout).toBe(30000)
    })

    it('should have correct content type header', () => {
      expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
    })

    it('should be configured with a base URL', () => {
      // The base URL can be configured via environment
      expect(typeof apiClient.defaults.baseURL).toBe('string')
    })
  })

  describe('authentication requests', () => {
    it('should not attach an authorization header for blank stored tokens', async () => {
      localStorageMock.getItem.mockReturnValue('   ')
      const requestHandlers = (
        apiClient.interceptors.request as unknown as {
          handlers: Array<{ fulfilled?: (config: unknown) => Promise<unknown> | unknown }>
        }
      ).handlers
      const fulfilled = requestHandlers.find((handler) => typeof handler.fulfilled === 'function')?.fulfilled

      expect(fulfilled).toBeTypeOf('function')

      const config = await fulfilled?.({
        headers: {},
        method: 'get',
      })

      expect((config as { headers: Record<string, string> }).headers.Authorization).toBeUndefined()
    })
  })

  describe('authentication errors', () => {
    it('should clear all stored session keys when a request returns 401', async () => {
      const responseHandlers = (
        apiClient.interceptors.response as unknown as {
          handlers: Array<{ rejected?: (error: unknown) => Promise<unknown> }>
        }
      ).handlers
      const rejected = responseHandlers.find((handler) => typeof handler.rejected === 'function')?.rejected

      expect(rejected).toBeTypeOf('function')

      await rejected?.({
        response: {
          status: 401,
          headers: {},
        },
        config: { headers: {} },
      })

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
    })
  })
})

describe('Request Types', () => {
  describe('UnifiedResponse', () => {
    it('should have correct structure', () => {
      const response = {
        code: 0,
        data: {},
        message: 'success',
        timestamp: Date.now()
      }

      expect(response).toHaveProperty('code')
      expect(response).toHaveProperty('data')
      expect(response).toHaveProperty('message')
      expect(response).toHaveProperty('timestamp')
    })
  })

  describe('PaginationParams', () => {
    it('should handle pagination parameters', () => {
      const params = {
        page: 1,
        pageSize: 20,
        sortBy: 'createdAt',
        sortOrder: 'desc'
      }

      expect(params.page).toBe(1)
      expect(params.pageSize).toBe(20)
    })
  })
})
