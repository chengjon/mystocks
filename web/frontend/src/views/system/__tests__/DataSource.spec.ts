import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  errorMock,
  getDataSourceConfigMock,
  lastRequestIdMock,
  loadingMock,
  updateDataSourceConfigMock,
} = vi.hoisted(() => ({
  errorMock: { value: null as string | null },
  getDataSourceConfigMock: vi.fn(),
  lastRequestIdMock: { value: '' },
  loadingMock: { value: false },
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
    loading: loadingMock,
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    exec: async (
      apiCall: () => Promise<{ success?: boolean; data?: unknown; request_id?: string; message?: string }>,
      options?: { errorMsg?: string }
    ) => {
      loadingMock.value = true
      errorMock.value = null

      try {
        const response = await apiCall()
        if (response?.request_id) {
          lastRequestIdMock.value = response.request_id
        }
        if (response?.success === false) {
          errorMock.value = response.message || options?.errorMsg || '请求失败'
          return null
        }
        return response?.data ?? response
      } finally {
        loadingMock.value = false
      }
    },
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoBadge: {
      template: '<span><slot /></span>',
    },
    ArtDecoButton: {
      props: ['disabled', 'loading'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<div><slot /></div>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<div><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></div>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
  }
})

import SystemDataSourcePage from '../DataSource.vue'

describe('SystemDataSource routed payload truth', () => {
  beforeEach(() => {
    loadingMock.value = false
    errorMock.value = null
    lastRequestIdMock.value = 'req-data-live'
    getDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
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
            status: 'active',
          },
        ],
      },
      request_id: 'req-data-live',
    })
    updateDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
      data: {},
    })
  })

  it('keeps stats-strip counts unresolved while the first config snapshot is still pending', async () => {
    let resolveConfig: ((value: {
      success: boolean
      data: {
        endpoints: Array<{
          endpoint_name: string
          description: string
          source_name: string
          status: string
        }>
      }
      request_id: string
    }) => void) | null = null

    getDataSourceConfigMock.mockImplementationOnce(() => new Promise((resolve) => {
      resolveConfig = resolve
    }))
    lastRequestIdMock.value = ''

    const wrapper = mount(SystemDataSourcePage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await nextTick()

    const statValuesBefore = wrapper.get('.stats-strip').findAll('.artdeco-stat-value').map((node) => node.text())
    expect(statValuesBefore).toEqual(['--', '--', 'ON', 'N/A'])
    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')

    resolveConfig?.({
      success: true,
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
            status: 'active',
          },
        ],
      },
      request_id: 'req-data-pending-late',
    })

    await flushPromises()

    const statValuesAfter = wrapper.get('.stats-strip').findAll('.artdeco-stat-value').map((node) => node.text())
    expect(statValuesAfter).toEqual(['2', '2', 'ON', 'req-data-pending-late'])
  })

  it('renders endpoint descriptions and endpoint identifiers when the live payload does not include url fields', async () => {
    const wrapper = mount(SystemDataSourcePage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('AKShare龙虎榜详情数据')
    expect(wrapper.text()).toContain('akshare.stock_lhb_detail_em')
    expect(wrapper.text()).toContain('Mock日线数据（用于测试和开发）')
    expect(wrapper.text()).toContain('mock.daily_kline')
    expect(wrapper.text()).not.toContain('N/A')
    expect(wrapper.text()).not.toContain('数据源名称启用端点操作akshare')
  })

  it('suppresses fabricated delta chrome and pseudo precision for count-or-label KPI cards', async () => {
    const wrapper = mount(SystemDataSourcePage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    const statsStrip = wrapper.get('.stats-strip')
    const statValues = statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())

    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statValues).toEqual(['2', '2', 'ON', 'req-data-live'])
    expect(statsStrip.text()).not.toContain('+0%')
    expect(statsStrip.text()).not.toContain('2.00')
  })

  it('does not fabricate a request id when the verified config snapshot has no request metadata', async () => {
    lastRequestIdMock.value = ''
    getDataSourceConfigMock.mockResolvedValueOnce({
      success: true,
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
            status: 'active',
          },
        ],
      },
      request_id: '',
    })

    const wrapper = mount(SystemDataSourcePage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.stats-strip').text()).toContain('当前请求N/A')
    expect(wrapper.text()).not.toMatch(/cfg-\d+/)
  })

  it('keeps the last verified request id and visible config rows when refresh fails after a successful sync', async () => {
    getDataSourceConfigMock
      .mockResolvedValueOnce({
        success: true,
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
              status: 'active',
            },
          ],
        },
        request_id: 'req-data-success',
      })
      .mockImplementation(async () => {
        lastRequestIdMock.value = 'req-data-refresh-fail'
        errorMock.value = '获取数据源配置失败'
        return { success: false }
      })

    const wrapper = mount(SystemDataSourcePage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-data-success')
    expect(wrapper.text()).toContain('AKShare龙虎榜详情数据')

    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-data-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-data-refresh-fail')
    expect(wrapper.get('.runtime-message').text()).toContain('获取数据源配置失败')
    expect(wrapper.get('.runtime-message').text()).toContain('当前仍显示上次成功同步的数据源配置快照。')
    expect(wrapper.text()).toContain('AKShare龙虎榜详情数据')
    expect(wrapper.text()).toContain('mock.daily_kline')
  })
})
