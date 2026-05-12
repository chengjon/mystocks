import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ArtDecoAlert from '@/components/artdeco/base/ArtDecoAlert.vue'

describe('ArtDecoAlert accessibility contract', () => {
  it('announces warning and error alerts assertively', () => {
    const warning = mount(ArtDecoAlert, {
      props: {
        type: 'warning',
        message: '风险阈值已触发'
      }
    })
    const error = mount(ArtDecoAlert, {
      props: {
        type: 'error',
        message: '交易提交失败'
      }
    })

    expect(warning.get('.artdeco-alert').attributes('role')).toBe('alert')
    expect(warning.get('.artdeco-alert').attributes('aria-live')).toBe('assertive')
    expect(error.get('.artdeco-alert').attributes('role')).toBe('alert')
    expect(error.get('.artdeco-alert').attributes('aria-live')).toBe('assertive')
  })

  it('announces informational and success alerts politely', () => {
    const info = mount(ArtDecoAlert, {
      props: {
        type: 'info',
        message: '数据同步完成'
      }
    })
    const success = mount(ArtDecoAlert, {
      props: {
        type: 'success',
        message: '策略保存成功'
      }
    })

    expect(info.get('.artdeco-alert').attributes('role')).toBe('status')
    expect(info.get('.artdeco-alert').attributes('aria-live')).toBe('polite')
    expect(success.get('.artdeco-alert').attributes('role')).toBe('status')
    expect(success.get('.artdeco-alert').attributes('aria-live')).toBe('polite')
  })
})
