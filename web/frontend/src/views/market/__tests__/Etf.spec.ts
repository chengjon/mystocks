import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Etf from '../Etf.vue'

describe('market/Etf legacy shell truth', () => {
  it('degrades the legacy ETF market page to an honest static shell when no canonical route owner exists', () => {
    const wrapper = mount(Etf as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('ETF 行情工作台')
    expect(wrapper.text()).toContain('当前 legacy ETF 行情页未接入可复用的一对一 canonical truth')
    expect(wrapper.text()).not.toContain('ETF MARKET DATA')
    expect(wrapper.text()).not.toContain('REFRESH ALL')
    expect(wrapper.text()).not.toContain('TOTAL ETF ASSETS')
    expect(wrapper.text()).not.toContain('TOP GAINERS')
    expect(wrapper.text()).not.toContain('沪深300ETF')
  })
})
