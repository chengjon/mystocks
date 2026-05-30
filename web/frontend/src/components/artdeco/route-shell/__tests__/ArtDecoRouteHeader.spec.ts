import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ArtDecoRouteHeader from '../ArtDecoRouteHeader.vue'

describe('ArtDecoRouteHeader', () => {
  it('renders the route shell classes, hooks, meta slot, and header actions', () => {
    const wrapper = mount(ArtDecoRouteHeader, {
      props: {
        title: '持仓工作台',
        subtitle: '统一查看持仓结构、盈亏表现和仓位分布',
        eyebrow: '持仓审阅',
        showStatus: true,
        statusText: 'LIVE',
        statusType: 'success',
        testId: 'trade-positions-header',
        legacyTest: 'trade-positions-header',
      },
      slots: {
        meta: '<span>请求: req-001</span><span>耗时: 12ms</span>',
        actions: '<button data-testid="trade-positions-refresh">刷新持仓</button>',
      },
    })

    expect(wrapper.classes()).toContain('artdeco-route-header')
    expect(wrapper.classes()).toContain('hero-shell')
    expect(wrapper.classes()).toContain('artdeco-card-shell')
    expect(wrapper.attributes('data-testid')).toBe('trade-positions-header')
    expect(wrapper.attributes('data-test')).toBe('trade-positions-header')
    expect(wrapper.find('.hero-eyebrow').text()).toBe('持仓审阅')
    expect(wrapper.find('.hero-meta').text()).toContain('请求: req-001')
    expect(wrapper.find('.header-title').text()).toBe('持仓工作台')
    expect(wrapper.find('.status-text').text()).toBe('LIVE')
    expect(wrapper.find('[data-testid="trade-positions-refresh"]').exists()).toBe(true)
  })
})
