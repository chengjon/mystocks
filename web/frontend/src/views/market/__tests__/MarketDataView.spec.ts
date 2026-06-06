import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import MarketDataView from '../MarketDataView.vue'

describe('market/MarketDataView legacy shell truth', () => {
  it('degrades the nested market-data aggregation workbench to an honest static shell when no one-to-one canonical owner exists', () => {
    const wrapper = mount(MarketDataView as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('市场数据聚合工作台')
    expect(wrapper.text()).toContain('当前 nested legacy 市场数据聚合页未接入可复用的一对一 canonical truth')
    expect(wrapper.text()).not.toContain('实时数据')
    expect(wrapper.text()).not.toContain('ETF行情')
    expect(wrapper.text()).not.toContain('竞价抢筹')
  })
})
