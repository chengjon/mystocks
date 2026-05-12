import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoInput from '@/components/artdeco/base/ArtDecoInput.vue'

describe('ArtDecoInput accessibility contract', () => {
  it('links helper text to the native input with aria-describedby', () => {
    const wrapper = mount(ArtDecoInput, {
      props: {
        modelValue: '',
        label: '股票代码',
        helperText: '请输入 6 位证券代码'
      }
    })

    const input = wrapper.get('input')
    const helper = wrapper.get('.artdeco-input__helper')

    expect(input.attributes('aria-describedby')).toBe(helper.attributes('id'))
    expect(input.attributes('aria-invalid')).toBeUndefined()
  })

  it('marks required and invalid states for assistive technology', () => {
    const wrapper = mount(ArtDecoInput, {
      props: {
        modelValue: '',
        label: '交易数量',
        required: true,
        errorMessage: '交易数量不能为空'
      }
    })

    const input = wrapper.get('input')
    const helper = wrapper.get('.artdeco-input__helper')

    expect(input.attributes('required')).toBeDefined()
    expect(input.attributes('aria-required')).toBe('true')
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(input.attributes('aria-describedby')).toBe(helper.attributes('id'))
  })
})
