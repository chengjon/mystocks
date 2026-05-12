import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoCollapsible from '@/components/artdeco/base/ArtDecoCollapsible.vue'

describe('ArtDecoCollapsible accessibility contract', () => {
  it('links the disclosure header with its controlled region', () => {
    const wrapper = mount(ArtDecoCollapsible, {
      props: {
        title: '筛选条件',
        expanded: true
      },
      slots: {
        default: '<p>筛选内容</p>'
      }
    })

    const header = wrapper.get('.artdeco-collapsible-header')
    const region = wrapper.get('.artdeco-collapsible-content')

    expect(header.attributes('role')).toBe('button')
    expect(header.attributes('tabindex')).toBe('0')
    expect(header.attributes('aria-expanded')).toBe('true')
    expect(header.attributes('aria-controls')).toBe(region.attributes('id'))
    expect(region.attributes('role')).toBe('region')
    expect(region.attributes('aria-labelledby')).toBe(header.attributes('id'))
  })

  it('marks disabled disclosures as unavailable and removes them from tab order', async () => {
    const wrapper = mount(ArtDecoCollapsible, {
      props: {
        title: '已锁定配置',
        disabled: true
      }
    })

    const header = wrapper.get('.artdeco-collapsible-header')

    expect(header.attributes('aria-disabled')).toBe('true')
    expect(header.attributes('tabindex')).toBe('-1')

    await header.trigger('click')
    await header.trigger('keydown', { key: 'Enter' })
    await header.trigger('keydown', { key: ' ' })

    expect(wrapper.emitted('toggle')).toBeUndefined()
    expect(wrapper.emitted('update:expanded')).toBeUndefined()
  })
})
