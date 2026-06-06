import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DatabaseMonitor from '../DatabaseMonitor.vue'

describe('DatabaseMonitor legacy shell truth', () => {
  it('degrades the pseudo-live database monitor dashboard to an honest static shell when no verified canonical owner exists', () => {
    const wrapper = mount(DatabaseMonitor as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('数据库监控工作台')
    expect(wrapper.text()).toContain('当前 legacy 数据库监控页未接入可复用的 canonical truth')
    expect(wrapper.text()).not.toContain('健康数据库')
    expect(wrapper.text()).not.toContain('数据分类总数')
    expect(wrapper.text()).not.toContain('架构简化历史')
    expect(wrapper.text()).not.toContain('Redis状态')
  })
})
