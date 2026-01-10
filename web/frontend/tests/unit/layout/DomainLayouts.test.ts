import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import BaseLayout from '@/layouts/BaseLayout.vue'
import BreadcrumbNav from '@/components/layout/BreadcrumbNav.vue'

// 导入所有域Layout组件
import MainLayout from '@/layouts/MainLayout.vue'
import MarketLayout from '@/layouts/MarketLayout.vue'
import DataLayout from '@/layouts/DataLayout.vue'
import RiskLayout from '@/layouts/RiskLayout.vue'
import StrategyLayout from '@/layouts/StrategyLayout.vue'
import MonitoringLayout from '@/layouts/MonitoringLayout.vue'

// 创建路由实例
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/dashboard', component: { template: '<div>Dashboard</div>' } },
    { path: '/market', component: { template: '<div>Market</div>' } },
    { path: '/analysis', component: { template: '<div>Analysis</div>' } },
    { path: '/risk', component: { template: '<div>Risk</div>' } },
    { path: '/strategy', component: { template: '<div>Strategy</div>' } },
    { path: '/monitoring', component: { template: '<div>Monitoring</div>' } }
  ]
})

describe('域Layout组件测试', () => {
  describe('MainLayout - Dashboard域', () => {
    it('应该渲染Dashboard菜单', () => {
      const wrapper = mount(MainLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      expect(baseLayout.exists()).toBe(true)
      expect(baseLayout.props('pageTitle')).toBe('Dashboard')
      
      const menuItems = baseLayout.props('menuItems')
      expect(menuItems).toHaveLength(4)
      expect(menuItems[0]).toEqual({
        path: '/dashboard',
        label: 'Overview',
        icon: '📊'
      })
    })

    it('应该包含正确的菜单项', () => {
      const wrapper = mount(MainLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      const menuItems = baseLayout.props('menuItems')
      
      const expectedPaths = ['/dashboard', '/dashboard/watchlist', '/dashboard/portfolio', '/dashboard/activity']
      const actualPaths = menuItems.map(item => item.path)
      
      expect(actualPaths).toEqual(expectedPaths)
    })
  })

  describe('MarketLayout - Market Data域', () => {
    it('应该渲染Market Data菜单', () => {
      const wrapper = mount(MarketLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      expect(baseLayout.exists()).toBe(true)
      expect(baseLayout.props('pageTitle')).toBe('Market Data')
      
      const menuItems = baseLayout.props('menuItems')
      expect(menuItems).toHaveLength(5)
      expect(menuItems[0].label).toBe('Stock List')
    })

    it('应该包含所有Market相关菜单项', () => {
      const wrapper = mount(MarketLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      const menuItems = baseLayout.props('menuItems')
      
      const expectedLabels = ['Stock List', 'Realtime', 'K-Line', 'Depth', 'Sector']
      const actualLabels = menuItems.map(item => item.label)
      
      expect(actualLabels).toEqual(expectedLabels)
    })
  })

  describe('DataLayout - Stock Analysis域', () => {
    it('应该渲染Stock Analysis菜单', () => {
      const wrapper = mount(DataLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      expect(baseLayout.exists()).toBe(true)
      expect(baseLayout.props('pageTitle')).toBe('Stock Analysis')
      
      const menuItems = baseLayout.props('menuItems')
      expect(menuItems).toHaveLength(5)
    })

    it('应该包含分析工具菜单项', () => {
      const wrapper = mount(DataLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      const menuItems = baseLayout.props('menuItems')
      
      const expectedLabels = ['Stock Screener', 'Industry', 'Concept', 'Fundamental', 'Technical']
      const actualLabels = menuItems.map(item => item.label)
      
      expect(actualLabels).toEqual(expectedLabels)
    })
  })

  describe('RiskLayout - Risk Monitor域', () => {
    it('应该渲染Risk Monitor菜单', () => {
      const wrapper = mount(RiskLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      expect(baseLayout.exists()).toBe(true)
      expect(baseLayout.props('pageTitle')).toBe('Risk Monitor')
      
      const menuItems = baseLayout.props('menuItems')
      expect(menuItems).toHaveLength(5)
    })

    it('应该包含风险管理菜单项', () => {
      const wrapper = mount(RiskLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      const menuItems = baseLayout.props('menuItems')
      
      const expectedLabels = ['Overview', 'Position Risk', 'Portfolio Risk', 'Alerts', 'Stress Test']
      const actualLabels = menuItems.map(item => item.label)
      
      expect(actualLabels).toEqual(expectedLabels)
    })
  })

  describe('StrategyLayout - Strategy Management域', () => {
    it('应该渲染Strategy Management菜单', () => {
      const wrapper = mount(StrategyLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      expect(baseLayout.exists()).toBe(true)
      expect(baseLayout.props('pageTitle')).toBe('Strategy Management')
      
      const menuItems = baseLayout.props('menuItems')
      expect(menuItems).toHaveLength(5)
    })

    it('应该包含策略管理菜单项', () => {
      const wrapper = mount(StrategyLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      const menuItems = baseLayout.props('menuItems')
      
      const expectedLabels = ['My Strategies', 'Market', 'Backtest', 'Signals', 'Performance']
      const actualLabels = menuItems.map(item => item.label)
      
      expect(actualLabels).toEqual(expectedLabels)
    })
  })

  describe('MonitoringLayout - Monitoring Platform域', () => {
    it('应该渲染Monitoring Platform菜单', () => {
      const wrapper = mount(MonitoringLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      expect(baseLayout.exists()).toBe(true)
      expect(baseLayout.props('pageTitle')).toBe('Monitoring Platform')
      
      const menuItems = baseLayout.props('menuItems')
      expect(menuItems).toHaveLength(5)
    })

    it('应该包含监控平台菜单项', () => {
      const wrapper = mount(MonitoringLayout, {
        global: {
          plugins: [router],
          components: { BreadcrumbNav }
        }
      })

      const baseLayout = wrapper.findComponent(BaseLayout)
      const menuItems = baseLayout.props('menuItems')
      
      const expectedLabels = ['Dashboard', 'Data Quality', 'Performance', 'API Health', 'Logs']
      const actualLabels = menuItems.map(item => item.label)
      
      expect(actualLabels).toEqual(expectedLabels)
    })
  })

  describe('所有Layout组件的共同特性', () => {
    const layouts = [
      { component: MainLayout, name: 'MainLayout' },
      { component: MarketLayout, name: 'MarketLayout' },
      { component: DataLayout, name: 'DataLayout' },
      { component: RiskLayout, name: 'RiskLayout' },
      { component: StrategyLayout, name: 'StrategyLayout' },
      { component: MonitoringLayout, name: 'MonitoringLayout' }
    ]

    it('所有Layout都应该包含BaseLayout', () => {
      layouts.forEach(({ component, name }) => {
        const wrapper = mount(component, {
          global: {
            plugins: [router],
            components: { BreadcrumbNav }
          }
        })

        const baseLayout = wrapper.findComponent(BaseLayout)
        expect(baseLayout.exists()).toBe(true)
      })
    })

    it('所有Layout都应该包含router-view slot', () => {
      layouts.forEach(({ component }) => {
        const wrapper = mount(component, {
          global: {
            plugins: [router],
            components: { BreadcrumbNav },
            stubs: {
              'router-view': { template: '<div class="router-view-stub"></div>' }
            }
          }
        })

        expect(wrapper.find('.router-view-stub').exists()).toBe(true)
      })
    })
  })
})
