import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'

const options = [
  { label: 'Realtime', value: 'realtime' },
  { label: 'History', value: 'history' }
]

describe('ArtDecoSelect accessibility contract', () => {
  it('uses the explicit label as the accessible name and hides the decorative icon', () => {
    const wrapper = mount(ArtDecoSelect, {
      props: {
        modelValue: 'realtime',
        options,
        label: 'Market data source',
        placeholder: 'Select data source'
      }
    })

    const select = wrapper.get('select')
    const icon = wrapper.get('.artdeco-select-icon')

    expect(select.attributes('aria-label')).toBe('Market data source')
    expect(icon.attributes('aria-hidden')).toBe('true')
  })

  it('marks disabled state for native and assistive technology consumers', () => {
    const wrapper = mount(ArtDecoSelect, {
      props: {
        modelValue: 'history',
        options,
        label: 'Backtest period',
        disabled: true
      }
    })

    const select = wrapper.get('select')

    expect(select.attributes('disabled')).toBeDefined()
    expect(select.attributes('aria-disabled')).toBe('true')
  })
})
