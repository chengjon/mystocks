import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/views/data/FundFlow.vue', () => ({
  default: defineComponent({
    name: 'MockFundFlowCanonicalPage',
    template: '<div class="canonical-fund-flow-page">资金流向工作台</div>',
  }),
}))

import CapitalFlow from '../CapitalFlow.vue'

describe('market/CapitalFlow legacy wrapper truth', () => {
  it('delegates the legacy capital-flow page to the canonical /data/fund-flow owner', () => {
    const wrapper = mount(CapitalFlow as never)

    expect(wrapper.find('.canonical-fund-flow-page').exists()).toBe(true)
    expect(wrapper.text()).toContain('资金流向工作台')
    expect(wrapper.text()).not.toContain('CAPITAL FLOW ANALYSIS')
    expect(wrapper.text()).not.toContain('REFRESH ALL')
    expect(wrapper.text()).not.toContain('TOTAL FLOW')
    expect(wrapper.text()).not.toContain('TOP GAINERS')
  })
})
