import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'

describe('ArtDecoCardCompact accessibility contract', () => {
  it('keeps non-clickable cards out of the tab order', () => {
    const wrapper = mount(ArtDecoCardCompact, {
      props: {
        title: '组合概览'
      }
    })

    const card = wrapper.get('.artdeco-card-compact')

    expect(card.attributes('role')).toBeUndefined()
    expect(card.attributes('tabindex')).toBeUndefined()
    expect(card.attributes('aria-label')).toBeUndefined()
  })

  it('exposes clickable cards as keyboard-operable buttons', async () => {
    const wrapper = mount(ArtDecoCardCompact, {
      props: {
        title: '订单详情',
        clickable: true
      }
    })

    const card = wrapper.get('.artdeco-card-compact')

    expect(card.attributes('role')).toBe('button')
    expect(card.attributes('tabindex')).toBe('0')
    expect(card.attributes('aria-label')).toBe('订单详情')

    await card.trigger('keydown', { key: 'Enter' })
    await card.trigger('keydown', { key: ' ' })

    expect(wrapper.emitted('click')).toHaveLength(2)
  })
})
