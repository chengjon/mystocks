import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ArtDecoCard from '../ArtDecoCard.vue'

describe('ArtDecoCard', () => {
  it('renders title, subtitle, body and footer content', () => {
    const wrapper = mount(ArtDecoCard as never, {
      props: {
        title: '卡片标题',
        subtitle: '卡片副标题',
      },
      slots: {
        default: '<div class="card-body-content">卡片内容</div>',
        footer: '<div class="card-footer-content">卡片底部</div>',
      },
    })

    expect(wrapper.text()).toContain('卡片标题')
    expect(wrapper.text()).toContain('卡片副标题')
    expect(wrapper.text()).toContain('卡片内容')
    expect(wrapper.text()).toContain('卡片底部')
    expect(wrapper.find('.artdeco-card__header').exists()).toBe(true)
    expect(wrapper.find('.artdeco-card__footer').exists()).toBe(true)
  })

  it('omits header and footer containers when neither title nor slots are provided', () => {
    const wrapper = mount(ArtDecoCard as never, {
      slots: {
        default: '<div class="card-body-content">卡片内容</div>',
      },
    })

    expect(wrapper.find('.artdeco-card__header').exists()).toBe(false)
    expect(wrapper.find('.artdeco-card__footer').exists()).toBe(false)
  })

  it('applies clickable, hoverable, variant and aspect ratio classes', () => {
    const wrapper = mount(ArtDecoCard as never, {
      props: {
        clickable: true,
        hoverable: true,
        variant: 'stat',
        aspectRatio: '16/9',
      },
    })

    const root = wrapper.get('.artdeco-card')

    expect(root.classes()).toContain('artdeco-card--clickable')
    expect(root.classes()).toContain('artdeco-card--hoverable')
    expect(root.classes()).toContain('artdeco-card--stat')
    expect(root.classes()).toContain('artdeco-card--aspect-16-9')
  })

  it('omits the hoverable class when hover affordance is disabled', () => {
    const wrapper = mount(ArtDecoCard as never, {
      props: {
        hoverable: false,
      },
    })

    expect(wrapper.get('.artdeco-card').classes()).not.toContain('artdeco-card--hoverable')
  })

  it('emits click only when clickable is enabled', async () => {
    const clickableWrapper = mount(ArtDecoCard as never, {
      props: {
        clickable: true,
      },
    })

    await clickableWrapper.trigger('click')
    expect(clickableWrapper.emitted('click')).toHaveLength(1)

    const normalWrapper = mount(ArtDecoCard as never, {
      props: {
        clickable: false,
      },
    })

    await normalWrapper.trigger('click')
    expect(normalWrapper.emitted('click')).toBeUndefined()
  })
})
