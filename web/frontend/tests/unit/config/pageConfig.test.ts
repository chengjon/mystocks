/**
 * Page Configuration System Tests
 * 
 * Tests for the extended page configuration model including:
 * - Type guards (isRouteName, isMonolithicConfig, isStandardConfig)
 * - Helper functions (getPageConfig, getTabConfig)
 * - Monolithic and standard page configurations
 * - Tab configuration access
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getPageConfig,
  getTabConfig,
  isRouteName,
  isMonolithicConfig,
  isStandardConfig,
  PAGE_CONFIG,
  TAB_CONFIGS,
  type PageConfig,
  type MonolithicPageConfig,
  type StandardPageConfig,
  type TabConfig
} from '@/config/pageConfig'

describe('Page Configuration System', () => {
  describe('Type Guards', () => {
    describe('isRouteName', () => {
      it('should return true for valid route names', () => {
        expect(isRouteName('dashboard')).toBe(true)
        expect(isRouteName('market-realtime')).toBe(true)
        expect(isRouteName('trading-signals')).toBe(true)
        expect(isRouteName('system-monitoring')).toBe(true)
      })

      it('should return false for invalid route names', () => {
        expect(isRouteName('invalid-route')).toBe(false)
        expect(isRouteName('')).toBe(false)
        expect(isRouteName('dashboard-extra')).toBe(false)
      })
    })

    describe('isMonolithicConfig', () => {
      it('should return true for monolithic configurations', () => {
        const config = PAGE_CONFIG['artdeco-market-data']
        expect(config).toBeDefined()
        if (config) {
          expect(isMonolithicConfig(config)).toBe(true)
        }
      })

      it('should return false for standard configurations', () => {
        const config = PAGE_CONFIG['dashboard']
        expect(config).toBeDefined()
        if (config) {
          expect(isMonolithicConfig(config)).toBe(false)
        }
      })
    })

    describe('isStandardConfig', () => {
      it('should return true for standard configurations', () => {
        const config = PAGE_CONFIG['dashboard']
        expect(config).toBeDefined()
        if (config) {
          expect(isStandardConfig(config)).toBe(true)
        }
      })

      it('should return false for monolithic configurations', () => {
        const config = PAGE_CONFIG['artdeco-market-data']
        expect(config).toBeDefined()
        if (config) {
          expect(isStandardConfig(config)).toBe(false)
        }
      })
    })
  })

  describe('getPageConfig', () => {
    it('should return configuration for valid route names', () => {
      const config = getPageConfig('dashboard')
      expect(config).toBeDefined()
      expect(config?.type).toBe('page')
      expect(config?.apiEndpoint).toBe('/api/dashboard/overview')
    })

    it('should return undefined for invalid route names', () => {
      const config = getPageConfig('nonexistent-route')
      expect(config).toBeUndefined()
    })

    it('should return monolithic configuration for market data routes', () => {
      const config = getPageConfig('artdeco-market-data')
      expect(config).toBeDefined()
      expect(config?.type).toBe('monolithic')
    })
  })

  describe('getTabConfig', () => {
    it('should return tab configuration for valid route and tab', () => {
      const tabConfig = getTabConfig('artdeco-market-data', 'realtime')
      expect(tabConfig).toBeDefined()
      expect(tabConfig?.id).toBe('realtime')
      expect(tabConfig?.apiEndpoint).toBe('/api/market/realtime')
      expect(tabConfig?.wsChannel).toBe('market:realtime')
    })

    it('should return undefined for invalid route', () => {
      const tabConfig = getTabConfig('invalid-route', 'realtime')
      expect(tabConfig).toBeUndefined()
    })

    it('should return undefined for non-monolithic route', () => {
      const tabConfig = getTabConfig('dashboard', 'overview')
      expect(tabConfig).toBeUndefined()
    })

    it('should return undefined for non-existent tab', () => {
      const tabConfig = getTabConfig('artdeco-market-data', 'nonexistent-tab')
      expect(tabConfig).toBeUndefined()
    })
  })

  describe('Standard Page Configurations', () => {
    it('should have valid API endpoints for dashboard routes', () => {
      const config = getPageConfig('dashboard')
      expect(config?.apiEndpoint).toBe('/api/dashboard/overview')
      expect(config?.wsChannel).toBe('dashboard:overview')
      expect(config?.component).toBe('DashboardPage')
    })

    it('should have valid API endpoints for trading routes', () => {
      const config = getPageConfig('trading-signals')
      expect(config?.apiEndpoint).toBe('/api/trading/signals')
      expect(config?.wsChannel).toBe('trading:signals')
    })

    it('should have valid API endpoints for risk routes', () => {
      const config = getPageConfig('risk-overview')
      expect(config?.apiEndpoint).toBe('/api/risk/overview')
      expect(config?.wsChannel).toBe('risk:overview')
    })

    it('should have valid API endpoints for system routes', () => {
      const config = getPageConfig('system-monitoring')
      expect(config?.apiEndpoint).toBe('/api/system/monitoring')
      expect(config?.wsChannel).toBe('system:monitoring')
    })
  })

  describe('Monolithic Page Configurations', () => {
    it('should have tabs for market data route', () => {
      const config = getPageConfig('artdeco-market-data')
      expect(config).toBeDefined()
      if (config && 'tabs' in config) {
        const monolithicConfig = config as MonolithicPageConfig
        expect(monolithicConfig.tabs).toBeDefined()
        expect(monolithicConfig.tabs.length).toBeGreaterThan(0)
      }
    })

    it('should have tabs for stock management route', () => {
      const config = getPageConfig('artdeco-stock-management')
      expect(config).toBeDefined()
      if (config && 'tabs' in config) {
        const monolithicConfig = config as MonolithicPageConfig
        expect(monolithicConfig.tabs).toBeDefined()
        expect(monolithicConfig.tabs.length).toBeGreaterThan(0)
      }
    })

    it('should have tabs for trading management route', () => {
      const config = getPageConfig('artdeco-trading-management')
      expect(config).toBeDefined()
      if (config && 'tabs' in config) {
        const monolithicConfig = config as MonolithicPageConfig
        expect(monolithicConfig.tabs).toBeDefined()
        expect(monolithicConfig.tabs.length).toBeGreaterThan(0)
      }
    })

    it('should reference valid TAB_CONFIGS for each tab', () => {
      const routes = ['artdeco-market-data', 'artdeco-stock-management', 'artdeco-trading-management']
      
      for (const route of routes) {
        const config = getPageConfig(route)
        expect(config).toBeDefined()
        
        if (config && 'tabs' in config) {
          const monolithicConfig = config as MonolithicPageConfig
          for (const tab of monolithicConfig.tabs) {
            const tabConfig = TAB_CONFIGS[tab.id]
            expect(tabConfig).toBeDefined()
            expect(tabConfig?.apiEndpoint).toBeDefined()
            expect(tabConfig?.wsChannel).toBeDefined()
          }
        }
      }
    })
  })

  describe('TAB_CONFIGS', () => {
    it('should have complete configuration for market tabs', () => {
      const tabs = ['realtime', 'technical', 'fund-flow', 'long-hub', 'institution', 'concepts', 'etf', 'screener']
      
      for (const tabId of tabs) {
        const config = TAB_CONFIGS[tabId]
        expect(config).toBeDefined()
        expect(config?.id).toBe(tabId)
        expect(config?.apiEndpoint).toBeDefined()
        expect(config?.wsChannel).toBeDefined()
      }
    })

    it('should have complete configuration for stock tabs', () => {
      const tabs = ['watchlist', 'positions', 'attribution', 'history', 'strategy', 'screener']
      
      for (const tabId of tabs) {
        const config = TAB_CONFIGS[tabId]
        expect(config).toBeDefined()
        expect(config?.id).toBe(tabId)
        expect(config?.apiEndpoint).toBeDefined()
        expect(config?.wsChannel).toBeDefined()
      }
    })

    it('should have complete configuration for trading tabs', () => {
      const tabs = ['signals', 'history', 'positions', 'attribution']
      
      for (const tabId of tabs) {
        const config = TAB_CONFIGS[tabId]
        expect(config).toBeDefined()
        expect(config?.id).toBe(tabId)
        expect(config?.apiEndpoint).toBeDefined()
        expect(config?.wsChannel).toBeDefined()
      }
    })
  })

  describe('Configuration Coverage', () => {
    it('should have configuration for all routes in router', () => {
      const routerRoutes = [
        'dashboard',
        'market-realtime',
        'market-technical',
        'market-fund-flow',
        'market-etf',
        'market-concept',
        'market-industry',
        'market-long-hub',
        'market-institution',
        'market-wencai',
        'market-screener',
        'strategy-overview',
        'strategy-backtest',
        'strategy-optimization',
        'strategy-analysis',
        'risk-overview',
        'risk-alerts',
        'risk-indicators',
        'risk-sentiment',
        'risk-announcement',
        'system-monitoring',
        'system-settings',
        'system-data-update',
        'system-data-quality',
        'system-api-health',
        'trading-signals',
        'trading-history',
        'trading-positions',
        'trading-attribution',
        'stock-management',
        'stock-portfolio',
        'artdeco-market-data',
        'artdeco-stock-management',
        'artdeco-trading-management'
      ]

      for (const route of routerRoutes) {
        const config = getPageConfig(route)
        expect(config).toBeDefined()
      }
    })
  })
})

describe('PageConfig Type Definitions', () => {
  it('should properly type monolithic configuration', () => {
    const config = getPageConfig('artdeco-market-data')
    expect(config).toBeDefined()
    
    if (config && isMonolithicConfig(config)) {
      const monolithicConfig = config as MonolithicPageConfig
      expect(monolithicConfig.type).toBe('monolithic')
      expect(monolithicConfig.component).toBe('ArtDecoMarketData')
      expect(monolithicConfig.tabs).toBeDefined()
    }
  })

  it('should properly type standard configuration', () => {
    const config = getPageConfig('dashboard')
    expect(config).toBeDefined()
    
    if (config && isStandardConfig(config)) {
      const standardConfig = config as StandardPageConfig
      expect(standardConfig.type).toBe('page')
      expect(standardConfig.apiEndpoint).toBe('/api/dashboard/overview')
      expect(standardConfig.wsChannel).toBe('dashboard:overview')
    }
  })

  it('should properly type tab configuration', () => {
    const tabConfig = getTabConfig('artdeco-market-data', 'realtime')
    expect(tabConfig).toBeDefined()
    
    if (tabConfig) {
      const typedTab = tabConfig as TabConfig
      expect(typedTab.id).toBe('realtime')
      expect(typedTab.apiEndpoint).toBe('/api/market/realtime')
      expect(typedTab.wsChannel).toBe('market:realtime')
    }
  })
})
