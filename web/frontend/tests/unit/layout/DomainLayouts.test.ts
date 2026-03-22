import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'
import MarketLayout from '@/layouts/MarketLayout.vue'
import DataLayout from '@/layouts/DataLayout.vue'
import RiskLayout from '@/layouts/RiskLayout.vue'
import StrategyLayout from '@/layouts/StrategyLayout.vue'
import MonitoringLayout from '@/layouts/MonitoringLayout.vue'
import {
  DASHBOARD_MENU_ITEMS,
  MARKET_MENU_ITEMS,
  ANALYSIS_MENU_ITEMS,
  RISK_MENU_ITEMS,
  STRATEGY_MENU_ITEMS,
  MONITORING_MENU_ITEMS
} from '@/layouts/archive/MenuConfig.ts'

const BaseLayoutStub = defineComponent({
  name: 'BaseLayout',
  props: {
    pageTitle: String,
    menuItems: {
      type: Array,
      default: () => []
    }
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'base-layout-stub' }, [
        h('div', { class: 'stub-page-title' }, props.pageTitle),
        h(
          'ul',
          { class: 'stub-menu-items' },
          (props.menuItems as Array<{ path: string; label: string }>).map((item) =>
            h('li', { class: 'stub-menu-item', 'data-path': item.path }, item.label),
          ),
        ),
        slots.default?.()
      ])
  }
})

const mountLayout = (component: unknown) =>
  mount(component as never, {
    global: {
      stubs: {
        BaseLayout: BaseLayoutStub,
        'router-view': { template: '<div class="router-view-stub"></div>' }
      }
    }
  })

describe('域Layout组件测试', () => {
  const layoutContracts = [
    {
      component: MainLayout,
      name: 'MainLayout',
      pageTitle: 'Dashboard',
      menuItems: DASHBOARD_MENU_ITEMS
    },
    {
      component: MarketLayout,
      name: 'MarketLayout',
      pageTitle: 'Market Data',
      menuItems: MARKET_MENU_ITEMS
    },
    {
      component: DataLayout,
      name: 'DataLayout',
      pageTitle: 'Stock Analysis',
      menuItems: ANALYSIS_MENU_ITEMS
    },
    {
      component: RiskLayout,
      name: 'RiskLayout',
      pageTitle: 'Risk Monitor',
      menuItems: RISK_MENU_ITEMS
    },
    {
      component: StrategyLayout,
      name: 'StrategyLayout',
      pageTitle: 'Strategy Management',
      menuItems: STRATEGY_MENU_ITEMS
    },
    {
      component: MonitoringLayout,
      name: 'MonitoringLayout',
      pageTitle: 'Monitoring Platform',
      menuItems: MONITORING_MENU_ITEMS
    }
  ]

  layoutContracts.forEach(({ component, name, pageTitle, menuItems }) => {
    describe(name, () => {
      it('应该将 pageTitle 和 menuItems 透传给 BaseLayout', () => {
        const wrapper = mountLayout(component)
        const baseLayout = wrapper.findComponent(BaseLayoutStub)

        expect(baseLayout.exists()).toBe(true)
        expect(baseLayout.props('pageTitle')).toBe(pageTitle)
        expect(baseLayout.props('menuItems')).toEqual(menuItems)
      })

      it('应该渲染 router-view slot', () => {
        const wrapper = mountLayout(component)

        expect(wrapper.find('.router-view-stub').exists()).toBe(true)
      })
    })
  })
})
