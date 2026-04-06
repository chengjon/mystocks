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

import SystemSettingsPage from '../Settings.vue'

describe('SystemSettings canonical page truth messaging', () => {
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

  it('explains the landed sectioned backend truth and keeps local draft fields explicitly non-canonical', async () => {
    const wrapper = mount(SystemSettingsPage as never, {
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

    expect(wrapper.text()).toContain('general 与 security 已接入系统级 /api/v1/system/settings/* 契约')
    expect(wrapper.text()).toContain('数据源配置使用系统级后端契约')
    expect(wrapper.text()).toContain('通知偏好使用用户级 /api/notification/preferences 契约')
    expect(wrapper.text()).toContain('下方“系统设置”表单仅保存本地设置草稿')
  })
})
