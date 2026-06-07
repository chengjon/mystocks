import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import BacktestKpiGrid from '../BacktestKpiGrid.vue'

describe('BacktestKpiGrid KPI truth', () => {
  it('does not render default change chrome for absolute backtest KPI cards', () => {
    const wrapper = mount(BacktestKpiGrid, {
      props: {
        items: [
          { label: '总回测次数', value: 12, variant: 'gold' },
          { label: '策略胜率', value: '58%', variant: 'rise' },
          { label: '年化收益', value: '16.4%', variant: 'gold' },
          { label: '最大回撤', value: '6.2%', variant: 'fall' },
        ],
      },
    })

    expect(wrapper.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).not.toContain('12.00')
    expect(wrapper.text()).not.toContain('+0%')
    expect(wrapper.text()).not.toContain('●')
  })
})
