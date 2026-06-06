import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Architecture from '../Architecture.vue'

describe('Architecture legacy shell truth', () => {
  it('degrades the pseudo-live architecture dashboard to an honest static shell when no verified canonical owner exists', () => {
    const wrapper = mount(Architecture as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('系统架构工作台')
    expect(wrapper.text()).toContain('当前 legacy 架构页未接入可复用的 canonical truth')
    expect(wrapper.text()).not.toContain('WEEK 3 SIMPLIFICATION')
    expect(wrapper.text()).not.toContain('双数据库架构')
    expect(wrapper.text()).not.toContain('4 → 2')
    expect(wrapper.text()).not.toContain('Redis 已完全移除')
  })
})
