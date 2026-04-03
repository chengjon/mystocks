import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getDetailedSystemHealthMock, getSystemHealthMock } = vi.hoisted(() => ({
  getDetailedSystemHealthMock: vi.fn(),
  getSystemHealthMock: vi.fn(),
}))

vi.mock('@/api', () => ({
  monitoringApi: {
    getDetailedSystemHealth: getDetailedSystemHealthMock,
    getSystemHealth: getSystemHealthMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    lastRequestId: { value: 'req-system-settings' },
    lastProcessTime: { value: '12.50' },
    exec: async (apiCall: () => Promise<{ success?: boolean; data?: unknown }>) => {
      const response = await apiCall()
      if (response?.success === false) {
        return null
      }
      return response?.data ?? response
    },
  }),
}))

import ArtDecoSystemSettings from '../ArtDecoSystemSettings.vue'

describe('ArtDecoSystemSettings', () => {
  beforeEach(() => {
    localStorage.clear()
    getDetailedSystemHealthMock.mockReset().mockResolvedValue({
      success: true,
      data: {
        metrics: [
          {
            endpoint: '/api/v1/market/quotes',
            qps: 53,
            p95: 128,
            error_rate: 0.18,
          },
        ],
      },
    })
    getSystemHealthMock.mockReset().mockResolvedValue({
      success: true,
      data: {
        status: 'healthy',
        service: 'mystocks-backend',
      },
    })
  })

  it('keeps the page explicitly degraded and saves only local settings', async () => {
    const wrapper = mount(ArtDecoSystemSettings as never, {
      global: {
        stubs: {
          ArtDecoButton: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
          },
          ArtDecoCard: {
            template: '<div><slot /></div>',
          },
          ArtDecoInput: {
            props: ['modelValue'],
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
          },
          ArtDecoStatCard: {
            props: ['label', 'value'],
            template: '<div>{{ label }} {{ value }}</div>',
          },
          ArtDecoTable: {
            props: ['data'],
            template: '<div class="hybrid-table">{{ JSON.stringify(data) }}</div>',
          },
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('统一系统配置后端契约仍未建立')
    expect(wrapper.text()).toContain('保存本地设置')

    const monitorTab = wrapper.findAll('button').find((button) => button.text() === '系统监控')
    const settingsTab = wrapper.findAll('button').find((button) => button.text() === '系统设置')

    expect(monitorTab).toBeTruthy()
    expect(settingsTab).toBeTruthy()

    await monitorTab!.trigger('click')
    expect(wrapper.text()).toContain('/api/v1/market/quotes')

    await settingsTab!.trigger('click')

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('http://127.0.0.1:9000')
    await wrapper.get('button').trigger('click')

    expect(localStorage.getItem('artdeco-system-settings')).toContain('127.0.0.1:9000')
  })
})
