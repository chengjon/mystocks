import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import MonitoringDashboard from './MonitoringDashboard.vue'

describe('MonitoringDashboard shell truth', () => {
  it('degrades the legacy pseudo-live dashboard to an honest static shell when no canonical monitoring truth exists', () => {
    const wrapper = mount(MonitoringDashboard as never)

    expect(wrapper.find('.legacy-static-shell').exists()).toBe(true)
    expect(wrapper.text()).toContain('监控中心')
    expect(wrapper.text()).toContain('当前 legacy 监控大盘未接入可复用的 canonical truth')
    expect(wrapper.text()).not.toContain('5216')
    expect(wrapper.text()).not.toContain('45')
    expect(wrapper.text()).not.toContain('实时监控数据')
    expect(wrapper.text()).not.toContain('CRITICAL ALERTS')
    expect(wrapper.text()).not.toContain('龙虎榜数据')
  })
})
