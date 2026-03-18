import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { describe, expect, it } from 'vitest'

import ArtDecoFilterBar from '../ArtDecoFilterBar.vue'

const ArtDecoSelectStub = defineComponent({
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template: '<button data-test="select-trigger" @click="$emit(\'update:modelValue\', \'SH\')">{{ modelValue }}</button>'
})

const ElSelectStub = defineComponent({
  props: {
    modelValue: {
      type: Array,
      default: undefined
    }
  },
  emits: ['change'],
  template: '<button data-test="multi-trigger" @click="$emit(\'change\', [\'tech\', \'ai\'])">multi</button>'
})

const ElDatePickerStub = defineComponent({
  props: {
    modelValue: {
      type: [String, Array, Date],
      default: undefined
    }
  },
  emits: ['change'],
  template: '<button data-test="date-trigger" @click="$emit(\'change\', [\'2026-03-01\', \'2026-03-31\'])">date</button>'
})

describe('ArtDecoFilterBar', () => {
  it('emits legacy change alongside filterChange for consumer compatibility', async () => {
    const wrapper = mount(ArtDecoFilterBar, {
      props: {
        filters: [
          {
            key: 'market',
            label: '市场',
            type: 'select',
            options: [
              { label: '上海', value: 'SH' },
              { label: '深圳', value: 'SZ' }
            ]
          }
        ]
      },
      global: {
        stubs: {
          ArtDecoSelect: ArtDecoSelectStub,
          'el-select': ElSelectStub,
          'el-option': true,
          'el-date-picker': ElDatePickerStub
        }
      }
    })

    await wrapper.get('[data-test="select-trigger"]').trigger('click')

    expect(wrapper.emitted('filterChange')).toBeTruthy()
    expect(wrapper.emitted('change')).toBeTruthy()
    expect(wrapper.emitted('filterChange')?.at(-1)?.[0]).toMatchObject({ market: 'SH' })
    expect(wrapper.emitted('change')?.at(-1)?.[0]).toMatchObject({ market: 'SH' })
  })

  it('passes multi-select and date-range values through filterChange payload', async () => {
    const wrapper = mount(ArtDecoFilterBar, {
      props: {
        filters: [
          {
            key: 'themes',
            label: '主题',
            type: 'multi-select',
            options: [
              { label: '科技', value: 'tech' },
              { label: 'AI', value: 'ai' }
            ]
          },
          {
            key: 'range',
            label: '区间',
            type: 'date-range'
          }
        ]
      },
      global: {
        stubs: {
          'el-select': ElSelectStub,
          'el-option': true,
          'el-date-picker': ElDatePickerStub
        }
      }
    })

    await wrapper.get('[data-test="multi-trigger"]').trigger('click')
    await wrapper.get('[data-test="date-trigger"]').trigger('click')

    const payload = wrapper.emitted('filterChange')?.at(-1)?.[0] as Record<string, unknown>

    expect(payload.themes).toEqual(['tech', 'ai'])
    expect(payload.range).toEqual(['2026-03-01', '2026-03-31'])
  })
})
