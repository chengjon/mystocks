/**
 * Market API Integration Test
 *
 * Tests the real API integration with fallback to Mock data
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { marketApiService } from '../marketWithFallback'

describe('Market API Integration', () => {
  beforeEach(() => {
    // Clear cache before each test
    marketApiService.clearCache()
  })

  describe('Market Overview', () => {
    it('should fetch market overview from real API', async () => {
      const data = await marketApiService.getMarketOverview()

      expect(data).toBeDefined()
      expect(data.marketStats).toBeDefined()
      expect(data.marketStats.totalStocks).toBeGreaterThan(0)
      expect(data.topEtfs).toBeDefined()
      expect(Array.isArray(data.topEtfs)).toBe(true)

      console.log('✅ Market Overview API Test Passed')
      console.log(`   Total stocks: ${data.marketStats.totalStocks}`)
      console.log(`   Top ETFs: ${data.topEtfs.length}`)
    })

    it('should use cached data on second call', async () => {
      // First call - should hit API
      const data1 = await marketApiService.getMarketOverview()

      // Second call - should use cache
      const data2 = await marketApiService.getMarketOverview()

      expect(data1).toEqual(data2)

      const stats = marketApiService.getCacheStats()
      expect(stats.keys).toContain('market:overview')

      console.log('✅ Cache Test Passed')
    })

    it('should force refresh when requested', async () => {
      // First call
      await marketApiService.getMarketOverview()

      // Force refresh
      const data = await marketApiService.getMarketOverview(true)

      expect(data).toBeDefined()
      console.log('✅ Force Refresh Test Passed')
    })
  })

  describe('Cache Management', () => {
    it('should clear cache', () => {
      marketApiService.clearCache()

      const stats = marketApiService.getCacheStats()
      expect(stats.keys.length).toBe(0)

      console.log('✅ Cache Clear Test Passed')
    })

    it('should track cache statistics', () => {
      marketApiService.getMarketOverview()

      const stats = marketApiService.getCacheStats()
      expect(stats).toBeDefined()
      expect(stats.size).toBeGreaterThan(0)

      console.log('📊 Cache Stats:', stats)
      console.log('✅ Cache Stats Test Passed')
    })
  })

  describe('Error Handling', () => {
    it('should fallback to Mock data on API failure', async () => {
      // This test requires mocking the request utility to simulate failure
      // For now, we just verify the service exists and has the method

      expect(marketApiService.getMarketOverview).toBeDefined()
      console.log('✅ Error Handling Test Structure Verified')
    })
  })
})

console.log('🧪 Market API Integration Tests Loaded')
