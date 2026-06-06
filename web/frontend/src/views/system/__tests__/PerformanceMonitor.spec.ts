import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import PerformanceMonitor from '../PerformanceMonitor.vue'

describe('PerformanceMonitor legacy shell truth', () => {
  it('degrades the pseudo-live performance monitor dashboard to an honest static shell when no verified canonical owner exists', () => {
    const wrapper = mount(PerformanceMonitor as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('性能监控工作台')
    expect(wrapper.text()).toContain('当前 legacy 性能监控页未接入可复用的 canonical truth')
    expect(wrapper.text()).not.toContain('CORE WEB VITALS')
    expect(wrapper.text()).not.toContain('性能预算')
    expect(wrapper.text()).not.toContain('优化建议')
    expect(wrapper.text()).not.toContain('Largest Contentful Paint')
  })
})
