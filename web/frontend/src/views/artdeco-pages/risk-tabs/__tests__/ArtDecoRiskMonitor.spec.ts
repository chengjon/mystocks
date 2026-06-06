import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/views/risk/Center.vue', () => ({
  default: {
    props: ['functionKey'],
    template: '<div class="risk-center-canonical-stub">risk {{ functionKey }}</div>',
  },
}))

import ArtDecoRiskMonitor from '../ArtDecoRiskMonitor.vue'

describe('ArtDecoRiskMonitor shell truth', () => {
  it('reuses the canonical risk center page instead of a placeholder migration shell', () => {
    const wrapper = mount(ArtDecoRiskMonitor as never, {
      attrs: {
        functionKey: 'risk-monitor',
      },
    })

    expect(wrapper.text()).not.toContain('风险监控主面板整理中')
    expect(wrapper.text()).not.toContain('STATUS: PLACEHOLDER')
    expect(wrapper.find('.risk-center-canonical-stub').exists()).toBe(true)
    expect(wrapper.find('.risk-center-canonical-stub').text()).toContain('risk-monitor')
  })
})
