import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Tdx from '../Tdx.vue'

describe('market/Tdx legacy shell truth', () => {
  it('degrades the legacy TDX data interface to an honest static shell when no verified canonical owner exists', () => {
    const wrapper = mount(Tdx as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('TDX 数据接口页')
    expect(wrapper.text()).toContain('未接入可复用的一对一 canonical truth')
    expect(wrapper.text()).not.toContain('REFRESH ALL')
    expect(wrapper.text()).not.toContain('TDX CONNECTED')
    expect(wrapper.text()).not.toContain('Response Time')
    expect(wrapper.text()).not.toContain('Active Sessions')
    expect(wrapper.text()).not.toContain('REAL-TIME QUOTES')
    expect(wrapper.text()).not.toContain('K-LINE CHART')
    expect(wrapper.text()).not.toContain('202.108.253.132')
  })
})
