import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  errorMock,
  getDetailedSystemHealthMock,
  getDataSourceConfigMock,
  getSystemGeneralSettingsMock,
  getSystemSecuritySettingsMock,
  getSystemHealthMock,
  lastProcessTimeMock,
  lastRequestIdMock,
  loadingMock,
  updateSystemGeneralSettingsMock,
  updateSystemSecuritySettingsMock,
} = vi.hoisted(() => {
  const { ref } = require('vue')

  return {
    errorMock: ref<string | null>(null),
    getDetailedSystemHealthMock: vi.fn(),
    getDataSourceConfigMock: vi.fn(),
    getSystemGeneralSettingsMock: vi.fn(),
    getSystemSecuritySettingsMock: vi.fn(),
    getSystemHealthMock: vi.fn(),
    lastProcessTimeMock: ref(''),
    lastRequestIdMock: ref(''),
    loadingMock: ref(false),
    updateSystemGeneralSettingsMock: vi.fn(),
    updateSystemSecuritySettingsMock: vi.fn(),
  }
})

vi.mock('@/api', () => ({
  monitoringApi: {
    getDetailedSystemHealth: getDetailedSystemHealthMock,
    getDataSourceConfig: getDataSourceConfigMock,
    getSystemGeneralSettings: getSystemGeneralSettingsMock,
    getSystemSecuritySettings: getSystemSecuritySettingsMock,
    getSystemHealth: getSystemHealthMock,
    updateSystemGeneralSettings: updateSystemGeneralSettingsMock,
    updateSystemSecuritySettings: updateSystemSecuritySettingsMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    lastProcessTime: lastProcessTimeMock,
    exec: async (
      apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string; process_time?: string }>
    ) => {
      loadingMock.value = true
      errorMock.value = null

      const response = await apiCall()
      lastRequestIdMock.value = response?.request_id ?? ''
      lastProcessTimeMock.value = response?.process_time ?? ''

      if (response?.success) {
        loadingMock.value = false
        return response.data ?? null
      }
      if (response && typeof response === 'object' && 'success' in response) {
        errorMock.value = response.message ?? '请求失败'
        loadingMock.value = false
        return null
      }
      loadingMock.value = false
      return null
    },
  }),
}))

import SystemSettingsPage from '../Settings.vue'

function createDeferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((res) => {
    resolve = res
  })
  return { promise, resolve }
}

function getTabButton(wrapper: ReturnType<typeof mount>, label: string) {
  const target = wrapper.findAll('button.tab').find((node) => node.text() === label)

  if (!target) {
    throw new Error(`Missing tab button: ${label}`)
  }

  return target
}

describe('SystemSettings canonical page truth messaging', () => {
  beforeEach(() => {
    localStorage.clear()
    errorMock.value = null
    lastRequestIdMock.value = ''
    lastProcessTimeMock.value = ''
    loadingMock.value = false
    getDetailedSystemHealthMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-system-monitor',
      process_time: '34.00',
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
      request_id: 'req-system-health',
      process_time: '15.00',
      data: {
        status: 'healthy',
        service: 'mystocks-backend',
      },
    })
    getDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-source-config',
      process_time: '18.00',
      data: {
        endpoints: [
          {
            endpoint_name: 'akshare.stock_lhb_detail_em',
            description: 'AKShare龙虎榜详情数据',
            source_name: 'akshare',
            status: 'active',
          },
          {
            endpoint_name: 'mock.daily_kline',
            description: 'Mock日线数据（用于测试和开发）',
            source_name: 'system_mock',
            status: 'maintenance',
          },
        ],
      },
    })
    getSystemGeneralSettingsMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-system-general',
      process_time: '12.50',
      data: {
        backend_url: 'http://localhost:8020',
        max_backtest_jobs: 4,
        default_slippage_percent: 0.05,
        fee_rate_bps: 2.5,
      },
    })
    getSystemSecuritySettingsMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-system-security',
      process_time: '16.00',
      data: {
        session_timeout_minutes: 120,
        mfa_required: false,
        ip_allowlist_enabled: false,
        password_policy_level: 'standard',
      },
    })
    updateSystemGeneralSettingsMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-system-general-save',
      process_time: '20.00',
      data: {
        backend_url: 'http://localhost:9123',
        max_backtest_jobs: 6,
        default_slippage_percent: 0.08,
        fee_rate_bps: 3.2,
      },
    })
    updateSystemSecuritySettingsMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-system-security-save',
      process_time: '24.00',
      data: {
        session_timeout_minutes: 90,
        mfa_required: true,
        ip_allowlist_enabled: true,
        password_policy_level: 'strict',
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
    await getTabButton(wrapper, '系统设置').trigger('click')
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

  it('loads security settings from the canonical backend and saves them through the security section contract', async () => {
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
    await getTabButton(wrapper, '安全设置').trigger('click')
    await flushPromises()

    const inputs = wrapper.findAll('input')
    expect(inputs).toHaveLength(3)
    expect((inputs[0].element as HTMLInputElement).value).toBe('120')
    expect((inputs[1].element as HTMLInputElement).checked).toBe(false)
    expect((inputs[2].element as HTMLInputElement).checked).toBe(false)
    expect((wrapper.get('select').element as HTMLSelectElement).value).toBe('standard')

    await inputs[0].setValue('90')
    await inputs[1].setValue(true)
    await inputs[2].setValue(true)
    await wrapper.get('select').setValue('strict')
    await wrapper.get('.page-header button').trigger('click')
    await flushPromises()

    expect(updateSystemSecuritySettingsMock).toHaveBeenCalledWith({
      session_timeout_minutes: 90,
      mfa_required: true,
      ip_allowlist_enabled: true,
      password_policy_level: 'strict',
    })
  })

  it('uses the live data-source config contract on the sources tab instead of sample inventory cards and rows', async () => {
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
          ArtDecoStatCard: false,
          ArtDecoTable: {
            props: ['data'],
            template: '<div class="hybrid-table">{{ JSON.stringify(data) }}</div>',
          },
        },
      },
    })

    await flushPromises()

    const statsGrid = wrapper.get('.stats-grid')
    const statValues = statsGrid.findAll('.artdeco-stat-value').map((node) => node.text())

    expect(statsGrid.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statValues.slice(0, 3)).toEqual(['2', '1', 'ON'])
    expect(wrapper.text()).toContain('AKShare龙虎榜详情数据')
    expect(wrapper.text()).toContain('akshare.stock_lhb_detail_em')
    expect(wrapper.text()).toContain('Mock日线数据（用于测试和开发）')
    expect(wrapper.text()).toContain('mock.daily_kline')
    expect(wrapper.text()).not.toContain('28,412')
    expect(wrapper.text()).not.toContain('3/4')
    expect(wrapper.text()).not.toContain('Wind')
    expect(statsGrid.text()).not.toContain('+0%')
    expect(statsGrid.text()).not.toContain('4.00')
    expect(statsGrid.text()).not.toContain('2.00')
  })

  it('does not present unresolved sources-tab counts as faux zero metrics before any verified config snapshot exists', async () => {
    const sourceDeferred = createDeferred<{
      success: true
      request_id: string
      process_time: string
      data: { endpoints: Array<Record<string, unknown>> }
    }>()

    getDataSourceConfigMock.mockReset().mockReturnValueOnce(sourceDeferred.promise)

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
          ArtDecoStatCard: false,
          ArtDecoTable: {
            props: ['data'],
            template: '<div class="hybrid-table">{{ JSON.stringify(data) }}</div>',
          },
        },
      },
    })

    await flushPromises()

    const headerMeta = wrapper.get('.header-meta').text()
    const statValues = wrapper.findAll('.stats-grid .artdeco-stat-value').map((node) => node.text())

    expect(headerMeta).toContain('DATA: PENDING')
    expect(headerMeta).toContain('REQ_ID: N/A')
    expect(headerMeta).toContain('TIME: N/A')
    expect(wrapper.get('.runtime-message').text()).toContain('数据源配置同步中...')
    expect(statValues).toEqual(['--', '--', 'ON', 'N/A'])
    expect(wrapper.find('.stats-grid').text()).not.toContain('0')

    sourceDeferred.resolve({
      success: true,
      request_id: 'req-source-config-late',
      process_time: '18.00',
      data: {
        endpoints: [
          {
            endpoint_name: 'akshare.stock_lhb_detail_em',
            description: 'AKShare龙虎榜详情数据',
            source_name: 'akshare',
            status: 'active',
          },
        ],
      },
    })
    await flushPromises()

    expect(wrapper.get('.header-meta').text()).toContain('DATA: REAL')
    expect(wrapper.findAll('.stats-grid .artdeco-stat-value').map((node) => node.text())).toEqual(['1', '1', 'ON', 'req-source-config-late'])
  })

  it('does not present embedded example monitor rows as live system telemetry when monitor APIs are unavailable', async () => {
    getDetailedSystemHealthMock.mockResolvedValueOnce({
      success: false,
      message: 'detailed health failed',
    })
    getSystemHealthMock.mockResolvedValueOnce({
      success: false,
      message: 'health failed',
    })

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
    await getTabButton(wrapper, '系统监控').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('DATA: UNAVAILABLE')
    expect(wrapper.text()).toContain('系统监控真实接口暂不可用，当前页面不再展示示例监控指标。')
    expect(wrapper.text()).toContain('暂无系统监控接口数据。')
    expect(wrapper.text()).not.toContain('/api/v1/market/quotes')
    expect(wrapper.text()).not.toContain('/api/v1/auth/login')
    expect(wrapper.text()).not.toContain('/api/v1/strategy/backtest')
  })

  it('uses plain health payload as a summary fallback instead of collapsing the monitor tab to unavailable', async () => {
    getDetailedSystemHealthMock.mockResolvedValueOnce({
      success: false,
      message: 'detailed health failed',
    })
    getSystemHealthMock.mockResolvedValueOnce({
      status: 'healthy',
      version: '1.0.0',
      timestamp: '2026-04-29T07:31:30.538Z',
    })

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
    await getTabButton(wrapper, '系统监控').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('DATA: SUMMARY')
    expect(wrapper.text()).toContain('系统健康接口已连通，但当前未返回 API 性能明细；下表仅展示健康摘要。')
    expect(wrapper.text()).toContain('/api/health')
    expect(wrapper.text()).not.toContain('DATA: UNAVAILABLE')
  })

  it('keeps the sources-tab header request metadata aligned with the visible sources snapshot when sibling loaders finish later', async () => {
    const sourceDeferred = createDeferred<{
      success: true
      request_id: string
      process_time: string
      data: { endpoints: Array<Record<string, unknown>> }
    }>()
    const monitorDeferred = createDeferred<{
      success: true
      request_id: string
      process_time: string
      data: { metrics: Array<Record<string, unknown>> }
    }>()
    const generalDeferred = createDeferred<{
      success: true
      request_id: string
      process_time: string
      data: {
        backend_url: string
        max_backtest_jobs: number
        default_slippage_percent: number
        fee_rate_bps: number
      }
    }>()

    getDataSourceConfigMock.mockReset().mockReturnValueOnce(sourceDeferred.promise)
    getDetailedSystemHealthMock.mockReset().mockReturnValueOnce(monitorDeferred.promise)
    getSystemGeneralSettingsMock.mockReset().mockReturnValueOnce(generalDeferred.promise)

    const wrapper = mount(SystemSettingsPage as never, {
      global: {
        stubs: {
          ArtDecoButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          ArtDecoCard: { template: '<div><slot /></div>' },
          ArtDecoInput: {
            props: ['modelValue'],
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
          },
          ArtDecoStatCard: false,
          ArtDecoTable: {
            props: ['data'],
            template: '<div class="hybrid-table">{{ JSON.stringify(data) }}</div>',
          },
        },
      },
    })

    sourceDeferred.resolve({
      success: true,
      request_id: 'req-source-config',
      process_time: '18.00',
      data: {
        endpoints: [
          {
            endpoint_name: 'akshare.stock_lhb_detail_em',
            description: 'AKShare龙虎榜详情数据',
            source_name: 'akshare',
            status: 'active',
          },
        ],
      },
    })
    await flushPromises()

    monitorDeferred.resolve({
      success: true,
      request_id: 'req-system-monitor-late',
      process_time: '34.00',
      data: {
        metrics: [
          { endpoint: '/api/v1/market/quotes', qps: 53, p95: 128, error_rate: 0.18 },
        ],
      },
    })
    generalDeferred.resolve({
      success: true,
      request_id: 'req-system-general-late',
      process_time: '12.50',
      data: {
        backend_url: 'http://localhost:8020',
        max_backtest_jobs: 4,
        default_slippage_percent: 0.05,
        fee_rate_bps: 2.5,
      },
    })
    await flushPromises()

    const headerMeta = wrapper.get('.header-meta').text()
    expect(headerMeta).toContain('DATA: REAL')
    expect(headerMeta).toContain('REQ_ID: req-source-config')
    expect(headerMeta).toContain('TIME: 18.00ms')
    expect(headerMeta).not.toContain('req-system-monitor-late')
    expect(headerMeta).not.toContain('req-system-general-late')
    expect(wrapper.text()).toContain('AKShare龙虎榜详情数据')
  })

  it('switches header request metadata with the active tab instead of pinning it to the last sibling loader that finished', async () => {
    const wrapper = mount(SystemSettingsPage as never, {
      global: {
        stubs: {
          ArtDecoButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          ArtDecoCard: { template: '<div><slot /></div>' },
          ArtDecoInput: {
            props: ['modelValue'],
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
          },
          ArtDecoStatCard: false,
          ArtDecoTable: {
            props: ['data'],
            template: '<div class="hybrid-table">{{ JSON.stringify(data) }}</div>',
          },
        },
      },
    })

    await flushPromises()

    const sourceMeta = wrapper.get('.header-meta').text()
    expect(sourceMeta).toContain('DATA: REAL')
    expect(sourceMeta).toContain('REQ_ID: req-source-config')
    expect(sourceMeta).toContain('TIME: 18.00ms')
    expect(wrapper.text()).toContain('AKShare龙虎榜详情数据')

    await getTabButton(wrapper, '系统监控').trigger('click')
    await flushPromises()

    const monitorMeta = wrapper.get('.header-meta').text()
    expect(monitorMeta).toContain('DATA: REAL')
    expect(monitorMeta).toContain('REQ_ID: req-system-monitor')
    expect(monitorMeta).toContain('TIME: 34.00ms')

    await getTabButton(wrapper, '系统设置').trigger('click')
    await flushPromises()

    const settingsMeta = wrapper.get('.header-meta').text()
    expect(settingsMeta).toContain('DATA: REAL')
    expect(settingsMeta).toContain('REQ_ID: req-system-general')
    expect(settingsMeta).toContain('TIME: 12.50ms')
  })
})
