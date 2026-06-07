import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/views/trade/History.vue', () => ({
  default: {
    props: ['functionKey', 'history'],
    template: `
      <div class="trade-history-canonical-stub">
        history {{ functionKey }} {{ Array.isArray(history) ? history.length : 'n/a' }}
      </div>
    `,
  },
}))

import ArtDecoHistoryView from '../ArtDecoHistoryView.vue'

describe('ArtDecoHistoryView shell truth', () => {
  it('reuses the canonical trade history page instead of maintaining a placeholder shell', () => {
    const wrapper = mount(ArtDecoHistoryView as never, {
      attrs: {
        functionKey: 'trade-history',
      },
    })

    expect(wrapper.text()).not.toContain('历史复盘主面板整理中')
    expect(wrapper.text()).not.toContain('MODE: TRADING CENTER')
    expect(wrapper.find('.trade-history-canonical-stub').exists()).toBe(true)
    expect(wrapper.find('.trade-history-canonical-stub').text()).toContain('trade-history')
    expect(wrapper.find('.trade-history-canonical-stub').text()).toContain('0')
  })
})
