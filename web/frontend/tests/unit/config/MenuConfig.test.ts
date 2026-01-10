import { describe, it, expect } from 'vitest'
import {
  DASHBOARD_MENU_ITEMS,
  MARKET_MENU_ITEMS,
  ANALYSIS_MENU_ITEMS,
  RISK_MENU_ITEMS,
  STRATEGY_MENU_ITEMS,
  MONITORING_MENU_ITEMS,
  MENU_CONFIG_MAP
} from '@/layouts/MenuConfig'

describe('MenuConfig.ts', () => {
  describe('菜单配置完整性', () => {
    it('Dashboard菜单应该有4个项', () => {
      expect(DASHBOARD_MENU_ITEMS).toHaveLength(4)
    })

    it('Market菜单应该有5个项', () => {
      expect(MARKET_MENU_ITEMS).toHaveLength(5)
    })

    it('Analysis菜单应该有5个项', () => {
      expect(ANALYSIS_MENU_ITEMS).toHaveLength(5)
    })

    it('Risk菜单应该有5个项', () => {
      expect(RISK_MENU_ITEMS).toHaveLength(5)
    })

    it('Strategy菜单应该有5个项', () => {
      expect(STRATEGY_MENU_ITEMS).toHaveLength(5)
    })

    it('Monitoring菜单应该有5个项', () => {
      expect(MONITORING_MENU_ITEMS).toHaveLength(5)
    })
  })

  describe('菜单项结构', () => {
    it('所有菜单项应该有必需的属性', () => {
      const allMenus = [
        ...DASHBOARD_MENU_ITEMS,
        ...MARKET_MENU_ITEMS,
        ...ANALYSIS_MENU_ITEMS,
        ...RISK_MENU_ITEMS,
        ...STRATEGY_MENU_ITEMS,
        ...MONITORING_MENU_ITEMS
      ]

      allMenus.forEach(item => {
        expect(item).toHaveProperty('path')
        expect(item).toHaveProperty('label')
        expect(item).toHaveProperty('icon')
        expect(item.path).toBeTruthy()
        expect(item.label).toBeTruthy()
        expect(item.icon).toBeTruthy()
      })
    })

    it('所有路径应该是绝对路径', () => {
      const allMenus = [
        ...DASHBOARD_MENU_ITEMS,
        ...MARKET_MENU_ITEMS,
        ...ANALYSIS_MENU_ITEMS,
        ...RISK_MENU_ITEMS,
        ...STRATEGY_MENU_ITEMS,
        ...MONITORING_MENU_ITEMS
      ]

      allMenus.forEach(item => {
        expect(item.path.startsWith('/')).toBe(true)
      })
    })
  })

  describe('菜单映射表', () => {
    it('MENU_CONFIG_MAP应该包含所有6个Layout', () => {
      const layoutNames = Object.keys(MENU_CONFIG_MAP)
      
      expect(layoutNames).toContain('MainLayout')
      expect(layoutNames).toContain('MarketLayout')
      expect(layoutNames).toContain('DataLayout')
      expect(layoutNames).toContain('RiskLayout')
      expect(layoutNames).toContain('StrategyLayout')
      expect(layoutNames).toContain('MonitoringLayout')
      expect(layoutNames).toHaveLength(6)
    })

    it('每个Layout应该映射到正确的菜单配置', () => {
      expect(MENU_CONFIG_MAP.MainLayout).toBe(DASHBOARD_MENU_ITEMS)
      expect(MENU_CONFIG_MAP.MarketLayout).toBe(MARKET_MENU_ITEMS)
      expect(MENU_CONFIG_MAP.DataLayout).toBe(ANALYSIS_MENU_ITEMS)
      expect(MENU_CONFIG_MAP.RiskLayout).toBe(RISK_MENU_ITEMS)
      expect(MENU_CONFIG_MAP.StrategyLayout).toBe(STRATEGY_MENU_ITEMS)
      expect(MENU_CONFIG_MAP.MonitoringLayout).toBe(MONITORING_MENU_ITEMS)
    })
  })
})
