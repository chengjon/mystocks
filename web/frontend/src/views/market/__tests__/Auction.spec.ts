import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Auction from '../Auction.vue'

describe('market/Auction legacy shell truth', () => {
  it('degrades the legacy auction bidding page to an honest static shell when no canonical route owner exists', () => {
    const wrapper = mount(Auction as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('竞价抢筹工作台')
    expect(wrapper.text()).toContain('当前 legacy 竞价抢筹页未接入可复用的一对一 canonical truth')
    expect(wrapper.text()).not.toContain('AUCTION BIDDING DATA')
    expect(wrapper.text()).not.toContain('REFRESH')
    expect(wrapper.text()).not.toContain('TOTAL AUCTION VOLUME')
    expect(wrapper.text()).not.toContain('PARTICIPATING STOCKS')
    expect(wrapper.text()).not.toContain('平安银行')
  })
})
