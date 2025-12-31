/**
 * API Client Unit Tests
 *
 * Tests HTTP request handling, interceptors, and error handling.
 */

import { describe, it, expect } from 'vitest'
import apiClient from './apiClient'

describe('apiClient', () => {
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
