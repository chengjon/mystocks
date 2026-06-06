import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ArtDecoRiskStatsGrid from '../ArtDecoRiskStatsGrid.vue'
import type { RiskMetrics } from '../riskManagementHelpers'

const unverifiedMetrics: RiskMetrics = {
  totalAssets: 0,
  totalAssetsChange: null,
  todayProfit: 0,
  todayProfitChange: null,
  maxDrawdown: null,
  sharpeRatio: null,
  volatility: null,
  beta: null,
  sortinoRatio: null,
  positionValue: 0,
}

describe('ArtDecoRiskStatsGrid', () => {
  it('marks unsupported risk metrics as unverified instead of rendering numeric placeholders', () => {
    const wrapper = mount(ArtDecoRiskStatsGrid as never, {
      props: {
        riskData: unverifiedMetrics,
      },
      global: {
        stubs: {
          ArtDecoIcon: {
            template: '<span />',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('最大回撤未校验待接入')
    expect(wrapper.text()).toContain('夏普比率未校验待接入')
    expect(wrapper.text()).toContain('年化波动率未校验待接入')
    expect(wrapper.text()).toContain('贝塔值未校验待接入')
    expect(wrapper.text()).toContain('索提诺比率未校验待接入')
    expect(wrapper.text()).not.toContain('最大回撤-0%')
    expect(wrapper.text()).not.toContain('夏普比率0')
    expect(wrapper.text()).not.toContain('年化波动率0%')
    expect(wrapper.text()).not.toContain('贝塔值1')
  })

  it('degrades unsupported holdings-derived change percentages instead of reusing total pnl ratio as faux change truth', () => {
    const wrapper = mount(ArtDecoRiskStatsGrid as never, {
      props: {
        riskData: {
          totalAssets: 1025000,
          totalAssetsChange: null,
          todayProfit: 55000,
          todayProfitChange: null,
          maxDrawdown: null,
          sharpeRatio: null,
          volatility: null,
          beta: null,
          sortinoRatio: null,
          positionValue: 1025000,
        } satisfies RiskMetrics,
      },
      global: {
        stubs: {
          ArtDecoIcon: {
            template: '<span />',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('总资产¥1,025,000待接入')
    expect(wrapper.text()).toContain('今日收益+¥55,000待接入')
    expect(wrapper.text()).not.toContain('+5.67%')
    expect(wrapper.text()).not.toContain('+0%')
  })
})
