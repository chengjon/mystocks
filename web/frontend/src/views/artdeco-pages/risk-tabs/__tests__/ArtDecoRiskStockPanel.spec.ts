import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ArtDecoRiskStockPanel from '../ArtDecoRiskStockPanel.vue'

const mountRiskStockPanel = () =>
  mount(ArtDecoRiskStockPanel as never, {
    global: {
      stubs: {
        ArtDecoCard: {
          template: `
            <section class="artdeco-card-stub">
              <div class="card-header"><slot name="header" /></div>
              <div class="card-body"><slot /></div>
            </section>
          `,
        },
        ArtDecoButton: {
          emits: ['click'],
          template: '<button class="artdeco-button-stub" @click="$emit(\'click\', $event)"><slot /></button>',
        },
        ArtDecoIcon: {
          template: '<span class="artdeco-icon-stub" />',
        },
      },
    },
  })

describe('ArtDecoRiskStockPanel', () => {
  it('degrades the single-name slice into explicit pending integration copy instead of implying live actionable analysis', () => {
    const wrapper = mountRiskStockPanel()

    expect(wrapper.text()).toContain('个股风险分析入口')
    expect(wrapper.text()).toContain('当前仅保留个股风险分析入口，个股级仓位、止损与波动联动待接入。')
    expect(wrapper.text()).toContain('当前路由仍复用组合级风险数据，不直接生成单标的风控动作。')
    expect(wrapper.text()).toContain('查看接入说明')
    expect(wrapper.text()).not.toContain('选择持仓股票查看详细风险分析')
    expect(wrapper.text()).not.toContain('选择股票')
  })

  it('emits the feedback event from the pending integration CTA', async () => {
    const wrapper = mountRiskStockPanel()

    await wrapper.get('.artdeco-button-stub').trigger('click')

    expect(wrapper.emitted('openStockModal')).toEqual([[]])
  })
})
