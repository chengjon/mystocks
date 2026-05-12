import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'

describe('ArtDecoSwitch accessibility contract', () => {
  it('exposes switch state and accessible name', () => {
    const wrapper = mount(ArtDecoSwitch, {
      props: {
        modelValue: true,
        label: '自动交易'
      }
    })

    const control = wrapper.get('.artdeco-switch-wrapper')

    expect(control.attributes('role')).toBe('switch')
    expect(control.attributes('aria-label')).toBe('自动交易')
    expect(control.attributes('aria-checked')).toBe('true')
    expect(control.attributes('tabindex')).toBe('0')
    expect(control.attributes('aria-disabled')).toBeUndefined()
  })

  it('supports keyboard activation with Enter and Space', async () => {
    const wrapper = mount(ArtDecoSwitch, {
      props: {
        modelValue: false,
        label: '实时刷新'
      }
    })

    const control = wrapper.get('.artdeco-switch-wrapper')

    await control.trigger('keydown', { key: 'Enter' })
    await control.trigger('keydown', { key: ' ' })

    expect(wrapper.emitted('update:modelValue')).toEqual([[true], [true]])
    expect(wrapper.emitted('change')).toEqual([[true], [true]])
  })

  it('removes keyboard activation when disabled', async () => {
    const wrapper = mount(ArtDecoSwitch, {
      props: {
        modelValue: false,
        label: '风控锁定',
        disabled: true
      }
    })

    const control = wrapper.get('.artdeco-switch-wrapper')

    expect(control.attributes('aria-disabled')).toBe('true')
    expect(control.attributes('tabindex')).toBe('-1')

    await control.trigger('keydown', { key: 'Enter' })
    await control.trigger('click')

    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
    expect(wrapper.emitted('change')).toBeUndefined()
  })
})
