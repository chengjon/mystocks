import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoProgress from '@/components/artdeco/base/ArtDecoProgress.vue'

describe('ArtDecoProgress accessibility contract', () => {
  it('exposes normalized progressbar semantics from title and value', () => {
    const wrapper = mount(ArtDecoProgress, {
      props: {
        title: '模型训练进度',
        value: 72.5
      }
    })

    const gauge = wrapper.get('.artdeco-progress__gauge')

    expect(gauge.attributes('role')).toBe('progressbar')
    expect(gauge.attributes('aria-label')).toBe('模型训练进度: 72.5%')
    expect(gauge.attributes('aria-valuemin')).toBe('0')
    expect(gauge.attributes('aria-valuemax')).toBe('100')
    expect(gauge.attributes('aria-valuenow')).toBe('72.5')
    expect(gauge.attributes('aria-valuetext')).toBe('72.5%')
  })

  it('clamps out-of-range values for assistive technology', () => {
    const wrapper = mount(ArtDecoProgress, {
      props: {
        title: '批处理完成度',
        value: 128
      }
    })

    const gauge = wrapper.get('.artdeco-progress__gauge')

    expect(gauge.attributes('aria-valuenow')).toBe('100')
    expect(gauge.attributes('aria-valuetext')).toBe('100.0%')
    expect(gauge.attributes('aria-label')).toBe('批处理完成度: 100.0%')
  })
})
