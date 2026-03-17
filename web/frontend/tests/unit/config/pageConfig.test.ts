import { describe, expect, it } from 'vitest'

import {
  PAGE_CONFIG,
  getPageConfig,
  getTabConfig,
  getTabsForComponent,
  isMonolithicConfig,
  isRouteName,
  isStandardConfig,
} from '../../../src/config/pageConfig'

describe('pageConfig current contract', () => {
  describe('route guards', () => {
    it('accepts current route names and rejects retired legacy route names', () => {
      expect(isRouteName('dashboard')).toBe(true)
      expect(isRouteName('market-fund-flow')).toBe(true)
      expect(isRouteName('stock-management')).toBe(true)

      expect(isRouteName('artdeco-market-data')).toBe(false)
      expect(isRouteName('artdeco-stock-management')).toBe(false)
      expect(isRouteName('invalid-route')).toBe(false)
    })
  })

  describe('page lookups', () => {
    it('returns current standard page config for dashboard', () => {
      const config = getPageConfig('dashboard')

      expect(config).toBeDefined()
      expect(config && isStandardConfig(config)).toBe(true)
      expect(config?.type).toBe('page')
      expect(config?.routePath).toBe('dashboard')
      expect(config?.apiEndpoint).toBeUndefined()
      expect(config?.component).toBe('ArtDecoDashboard.vue')
    })

    it('returns current monolithic config for market fund flow', () => {
      const config = getPageConfig('market-fund-flow')

      expect(config).toBeDefined()
      expect(config && isMonolithicConfig(config)).toBe(true)
      expect(config?.type).toBe('monolithic')
      expect(config?.routePath).toBe('fund-flow')
      expect(config?.component).toBe('ArtDecoMarketData.vue')
      expect(config?.tabs.length).toBeGreaterThan(0)
    })

    it('does not expose retired legacy keys in PAGE_CONFIG', () => {
      expect(PAGE_CONFIG['artdeco-market-data']).toBeUndefined()
      expect(PAGE_CONFIG['artdeco-stock-management']).toBeUndefined()
      expect(PAGE_CONFIG['artdeco-trading-management']).toBeUndefined()
    })
  })

  describe('tab lookups', () => {
    it('returns current tab config for a monolithic route', () => {
      const tabConfig = getTabConfig('market-fund-flow', 'fund-flow')

      expect(tabConfig).toBeDefined()
      expect(tabConfig?.id).toBe('fund-flow')
      expect(tabConfig?.apiEndpoint).toBe('/api/market/fund-flow')
      expect(tabConfig?.wsChannel).toBe('market:fund-flow')
    })

    it('returns undefined for standard routes or invalid tabs', () => {
      expect(getTabConfig('dashboard', 'overview')).toBeUndefined()
      expect(getTabConfig('market-fund-flow', 'nonexistent-tab')).toBeUndefined()
      expect(getTabConfig('invalid-route', 'fund-flow')).toBeUndefined()
    })

    it('returns tabs by component for the generated monolithic components', () => {
      const marketTabs = getTabsForComponent('ArtDecoMarketData.vue')
      const stockTabs = getTabsForComponent('ArtDecoStockManagement.vue')

      expect(marketTabs.map(tab => tab.id)).toEqual(['fund-flow', 'etf', 'concepts', 'lhb', 'auction', 'institution'])
      expect(stockTabs.map(tab => tab.id)).toEqual(['overview', 'watchlist', 'positions', 'attribution', 'history', 'strategy'])
      expect(getTabsForComponent('UnknownComponent.vue')).toEqual([])
    })
  })
})
