import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ArtDecoButton from '../ArtDecoButton.vue'

describe('ArtDecoButton', () => {
  it('renders button text, icon slot, and loading spinner state', () => {
    const wrapper = mount(ArtDecoButton as never, {
      props: {
        loading: true,
      },
      slots: {
        default: '提交',
        icon: '<span class="icon-content">ICON</span>',
      },
    })

    expect(wrapper.text()).toContain('提交')
    expect(wrapper.find('.artdeco-button__icon').exists()).toBe(true)
    expect(wrapper.find('.icon-content').exists()).toBe(true)
    expect(wrapper.find('.artdeco-button__spinner').exists()).toBe(true)
    expect(wrapper.attributes('aria-busy')).toBe('true')
  })

  it('maps default and normalized solid variants correctly', () => {
    const defaultWrapper = mount(ArtDecoButton as never, {
      slots: { default: '默认按钮' },
    })

    expect(defaultWrapper.classes()).toContain('artdeco-button--default')

    const primaryWrapper = mount(ArtDecoButton as never, {
      props: { variant: 'primary' },
      slots: { default: '主按钮' },
    })

    expect(primaryWrapper.classes()).toContain('artdeco-button--solid')
    expect(primaryWrapper.classes()).not.toContain('artdeco-button--primary')

    const goldWrapper = mount(ArtDecoButton as never, {
      props: { variant: 'gold' },
      slots: { default: '金色按钮' },
    })

    expect(goldWrapper.classes()).toContain('artdeco-button--solid')
    expect(goldWrapper.classes()).not.toContain('artdeco-button--gold')
  })

  it('applies size, block, priority, and motion classes', () => {
    const wrapper = mount(ArtDecoButton as never, {
      props: {
        size: 'lg',
        block: true,
        priority: 'secondary',
        motion: 'data',
      },
      slots: { default: '扩展按钮' },
    })

    expect(wrapper.classes()).toContain('artdeco-button--lg')
    expect(wrapper.classes()).toContain('artdeco-button--block')
    expect(wrapper.classes()).toContain('artdeco-button--priority-secondary')
    expect(wrapper.classes()).toContain('artdeco-button--motion-data')
  })

  it('disables click emit when disabled or loading, but emits normally otherwise', async () => {
    const enabledWrapper = mount(ArtDecoButton as never, {
      slots: { default: '启用按钮' },
    })

    await enabledWrapper.trigger('click')
    expect(enabledWrapper.emitted('click')).toHaveLength(1)

    const disabledWrapper = mount(ArtDecoButton as never, {
      props: { disabled: true },
      slots: { default: '禁用按钮' },
    })

    expect(disabledWrapper.attributes('disabled')).toBeDefined()
    await disabledWrapper.trigger('click')
    expect(disabledWrapper.emitted('click')).toBeUndefined()

    const loadingWrapper = mount(ArtDecoButton as never, {
      props: { loading: true },
      slots: { default: '加载按钮' },
    })

    expect(loadingWrapper.attributes('disabled')).toBeDefined()
    await loadingWrapper.trigger('click')
    expect(loadingWrapper.emitted('click')).toBeUndefined()
  })
})
