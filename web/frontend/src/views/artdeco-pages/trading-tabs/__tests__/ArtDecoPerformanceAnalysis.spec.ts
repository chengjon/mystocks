import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/views/trade/Portfolio.vue', () => ({
  default: {
    props: ['functionKey'],
    template: '<div class="trade-portfolio-canonical-stub">portfolio {{ functionKey }}</div>',
  },
}))

import ArtDecoPerformanceAnalysis from '../ArtDecoPerformanceAnalysis.vue'

describe('ArtDecoPerformanceAnalysis shell truth', () => {
  it('reuses the canonical trade portfolio page instead of maintaining a placeholder shell', () => {
    const wrapper = mount(ArtDecoPerformanceAnalysis as never, {
      attrs: {
        functionKey: 'trade-portfolio',
      },
    })

    expect(wrapper.text()).not.toContain('绩效分析主面板整理中')
    expect(wrapper.text()).not.toContain('MODE: TRADING CENTER')
    expect(wrapper.find('.trade-portfolio-canonical-stub').exists()).toBe(true)
    expect(wrapper.find('.trade-portfolio-canonical-stub').text()).toContain('trade-portfolio')
  })
})
