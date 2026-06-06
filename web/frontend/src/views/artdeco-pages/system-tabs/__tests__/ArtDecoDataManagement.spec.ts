import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getDataSourceConfigMock, updateDataSourceConfigMock } = vi.hoisted(() => ({
  getDataSourceConfigMock: vi.fn(),
  updateDataSourceConfigMock: vi.fn(),
}))

vi.mock('@/api/index', () => ({
  monitoringApi: {
    getDataSourceConfig: getDataSourceConfigMock,
    updateDataSourceConfig: updateDataSourceConfigMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: { value: false },
    error: { value: null },
    lastRequestId: { value: 'req-ds' },
    exec: async (apiCall: () => Promise<unknown>) => {
      const response = await apiCall()
      if (response && typeof response === 'object' && 'success' in response && (response as { success: boolean }).success === false) {
        return null
      }
      return (response as { data?: unknown })?.data ?? response
    },
  }),
}))

const mockConfigItems = [
  { name: 'akshare', enabled: true, endpoint: 'https://ak.example/api', endpointName: 'akshare.stock_zh_a_hist' },
  { name: 'tushare', enabled: false, endpoint: 'https://ts.example/api', endpointName: 'tushare.daily' },
]

vi.mock('@/views/artdeco-pages/system-tabs/dataManagementData', () => ({
  extractDataSourceConfigItems: () => mockConfigItems,
  NormalizedDataSourceConfigItem: undefined,
}))

vi.mock('@/views/artdeco-pages/system-tabs/dataManagementCapabilities', () => ({
  supportsDataSourceConfigWrite: () => true,
  buildDataSourceConfigBatchRequest: () => ({
    operations: [{ action: 'update', endpoint_name: 'test', updates: { status: 'active' } }],
  }),
}))

import ArtDecoDataManagement from '../ArtDecoDataManagement.vue'

const stubs = {
  ArtDecoCard: { template: '<div><slot name="header" /><slot /></div>' },
  ArtDecoButton: {
    props: ['disabled', 'loading', 'variant', 'size'],
    template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><template v-if="$slots.icon"><slot name="icon" /></template></button>',
  },
  ArtDecoHeader: {
    props: ['title', 'subtitle', 'showStatus', 'statusText', 'statusType'],
    template: '<div><slot name="actions" /></div>',
  },
  ArtDecoIcon: { template: '<span />' },
  ArtDecoStatCard: {
    props: ['label', 'value', 'variant'],
    template: '<div>{{ label }} {{ value }}</div>',
  },
}

describe('ArtDecoDataManagement', () => {
  beforeEach(() => {
    getDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
      code: 200,
      data: {
        endpoints: [
          {
            endpoint_name: 'akshare.stock_zh_a_hist',
            source_name: 'akshare',
            status: 'active',
            url: 'https://ak.example/api',
          },
          {
            endpoint_name: 'tushare.daily',
            source_name: 'tushare',
            status: 'maintenance',
            url: 'https://ts.example/api',
          },
        ],
      },
    })
    updateDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
      code: 200,
      data: {},
    })
  })

  it('renders config rows from endpoints payload', async () => {
    const wrapper = mount(ArtDecoDataManagement as never, {
      global: {
        directives: { loading: { mounted() {} } },
        stubs,
      },
    })

    await flushPromises()

    expect(getDataSourceConfigMock).toHaveBeenCalled()
    expect(wrapper.text()).toContain('akshare')
    expect(wrapper.text()).toContain('https://ak.example/api')
    expect(wrapper.text()).toContain('tushare')
    expect(wrapper.text()).toContain('https://ts.example/api')
  })

  it('renders toggle and save buttons for data source management', async () => {
    const wrapper = mount(ArtDecoDataManagement as never, {
      global: {
        directives: { loading: { mounted() {} } },
        stubs,
      },
    })

    await flushPromises()

    const buttonTexts = wrapper.findAll('button').map((b) => b.text())

    // Enabled item shows "禁用" toggle, disabled item shows "启用" toggle
    expect(buttonTexts.some((t) => t.includes('禁用'))).toBe(true)
    expect(buttonTexts.some((t) => t.includes('启用'))).toBe(true)

    // Action bar buttons
    expect(buttonTexts.some((t) => t.includes('保存配置'))).toBe(true)
    expect(buttonTexts.some((t) => t.includes('刷新'))).toBe(true)
    expect(buttonTexts.some((t) => t.includes('恢复默认'))).toBe(true)
  })
})
