import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getDetailedSystemHealthMock, getSystemHealthMock, getSystemGeneralSettingsMock, updateSystemGeneralSettingsMock } = vi.hoisted(() => ({
  getDetailedSystemHealthMock: vi.fn(),
  getSystemHealthMock: vi.fn(),
  getSystemGeneralSettingsMock: vi.fn(),
  updateSystemGeneralSettingsMock: vi.fn(),
}))

vi.mock('@/api', () => ({
  monitoringApi: {
    getDetailedSystemHealth: getDetailedSystemHealthMock,
    getSystemHealth: getSystemHealthMock,
    getSystemGeneralSettings: getSystemGeneralSettingsMock,
    updateSystemGeneralSettings: updateSystemGeneralSettingsMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    lastRequestId: { value: 'req-system-settings' },
    lastProcessTime: { value: '12.50' },
    loading: { value: false },
    exec: async (apiCall: () => Promise<unknown>) => {
      const response = await apiCall()
      if (response && typeof response === 'object' && 'success' in response && (response as { success: boolean }).success === false) {
        return null
      }
      return (response as { data?: unknown })?.data ?? response
    },
  }),
}))

vi.mock('@/config/runtime-endpoints', () => ({
  API_BASE_URL: 'http://127.0.0.1:8020',
}))

vi.mock('@/views/artdeco-pages/system-tabs/systemSettingsMonitorData', () => ({
  normalizeSystemSettingsMonitorRows: (data: unknown) => {
    const d = data as { data?: { metrics?: unknown[] } }
    if (d?.data?.metrics) {
      return (d.data.metrics as { endpoint: string; qps: number; p95: number; error_rate: number }[]).map((m) => ({
        endpoint: m.endpoint,
        qps: m.qps,
        p95: m.p95,
        errorRate: `${m.error_rate}%`,
      }))
    }
    return []
  },
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
    getSystemGeneralSettingsMock.mockReset().mockResolvedValue({
      backend_url: 'http://127.0.0.1:8020',
      max_backtest_jobs: 4,
      default_slippage_percent: 0.05,
      fee_rate_bps: 2.5,
    })
    updateSystemGeneralSettingsMock.mockReset().mockResolvedValue({
      backend_url: 'http://127.0.0.1:8020',
      max_backtest_jobs: 4,
      default_slippage_percent: 0.05,
      fee_rate_bps: 2.5,
    })
  })

  it('renders the system settings page with tabs and monitor data', async () => {
    const wrapper = mount(ArtDecoSystemSettings as never, {
      global: {
        stubs: {
          ArtDecoButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          ArtDecoCard: { template: '<div><slot /></div>' },
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

    // Verify title and key rendered text from Settings.vue
    expect(wrapper.text()).toContain('系统配置中心')
    expect(wrapper.text()).toContain('保存系统设置')

    // Verify tabs exist
    const sourcesTab = wrapper.findAll('button').find((button) => button.text() === '数据源')
    const settingsTab = wrapper.findAll('button').find((button) => button.text() === '系统设置')
    const monitorTab = wrapper.findAll('button').find((button) => button.text() === '系统监控')

    expect(sourcesTab).toBeTruthy()
    expect(settingsTab).toBeTruthy()
    expect(monitorTab).toBeTruthy()

    // Verify monitor tab shows API data
    await monitorTab!.trigger('click')
    expect(wrapper.text()).toContain('/api/v1/market/quotes')
  })

  it('saves settings via API when save button clicked', async () => {
    const wrapper = mount(ArtDecoSystemSettings as never, {
      global: {
        stubs: {
          ArtDecoButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          ArtDecoCard: { template: '<div><slot /></div>' },
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

    // Navigate to settings tab
    const settingsTab = wrapper.findAll('button').find((button) => button.text() === '系统设置')
    await settingsTab!.trigger('click')

    // Find and click the save button (the one with "保存系统设置" text)
    const allButtons = wrapper.findAll('button')
    const saveButton = allButtons.find((b) => b.text().includes('保存系统设置'))
    expect(saveButton).toBeTruthy()
    await saveButton!.trigger('click')
    await flushPromises()

    // Verify API was called to save
    expect(updateSystemGeneralSettingsMock).toHaveBeenCalled()
  })
})
