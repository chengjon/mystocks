import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getDetailedSystemHealthMock,
  getSystemGeneralSettingsMock,
  getSystemHealthMock,
  updateSystemGeneralSettingsMock,
} = vi.hoisted(() => ({
  getDetailedSystemHealthMock: vi.fn(),
  getSystemGeneralSettingsMock: vi.fn(),
  getSystemHealthMock: vi.fn(),
  updateSystemGeneralSettingsMock: vi.fn(),
}))

vi.mock('@/api', () => ({
  monitoringApi: {
    getDetailedSystemHealth: getDetailedSystemHealthMock,
    getSystemGeneralSettings: getSystemGeneralSettingsMock,
    getSystemHealth: getSystemHealthMock,
    updateSystemGeneralSettings: updateSystemGeneralSettingsMock,
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
    getSystemGeneralSettingsMock.mockReset().mockResolvedValue({
      success: true,
      data: {
        backend_url: 'http://localhost:8020',
        max_backtest_jobs: 4,
        default_slippage_percent: 0.05,
        fee_rate_bps: 2.5,
      },
    })
    updateSystemGeneralSettingsMock.mockReset().mockResolvedValue({
      success: true,
      data: {
        backend_url: 'http://localhost:9123',
        max_backtest_jobs: 6,
        default_slippage_percent: 0.08,
        fee_rate_bps: 3.2,
      },
    })
  })

  it('loads general settings from the canonical backend and saves without local fallback persistence', async () => {
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
    await wrapper.get('button.tab:nth-of-type(2)').trigger('click')
    await flushPromises()

    const inputs = wrapper.findAll('input')
    expect(inputs).toHaveLength(4)
    expect((inputs[0].element as HTMLInputElement).value).toBe('http://localhost:8020')
    expect((inputs[1].element as HTMLInputElement).value).toBe('4')
    expect((inputs[2].element as HTMLInputElement).value).toBe('0.05')
    expect((inputs[3].element as HTMLInputElement).value).toBe('2.5')

    expect(wrapper.text()).toContain('general 与 security 已接入系统级 /api/v1/system/settings/* 契约')
    expect(wrapper.text()).toContain('数据源配置使用系统级后端契约')
    expect(wrapper.text()).toContain('通知偏好使用用户级 /api/notification/preferences 契约')
    expect(wrapper.text()).toContain('下方“系统设置”表单直接写入 general section 的系统级后端真相')

    await inputs[0].setValue('http://localhost:9123')
    await inputs[1].setValue('6')
    await inputs[2].setValue('0.08')
    await inputs[3].setValue('3.2')
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(updateSystemGeneralSettingsMock).toHaveBeenCalledWith({
      backend_url: 'http://localhost:9123',
      max_backtest_jobs: 6,
      default_slippage_percent: 0.08,
      fee_rate_bps: 3.2,
    })
    expect(localStorage.getItem('artdeco-system-settings')).toBeNull()
  })
})
