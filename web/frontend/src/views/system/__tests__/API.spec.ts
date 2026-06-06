import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getDetailedSystemHealthMock,
  getSystemHealthMock,
  errorMock,
  loadingMock,
  lastRequestIdMock,
} = vi.hoisted(() => ({
  getDetailedSystemHealthMock: vi.fn(),
  getSystemHealthMock: vi.fn(),
  errorMock: { value: null as string | null },
  loadingMock: { value: false },
  lastRequestIdMock: { value: '' },
}))

vi.mock('@/api/index', () => ({
  monitoringApi: {
    getSystemHealth: getSystemHealthMock,
    getDetailedSystemHealth: getDetailedSystemHealthMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    exec: async (
      apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string }>,
      options: { errorMsg?: string } = {}
    ) => {
      errorMock.value = null
      const response = await apiCall()
      lastRequestIdMock.value = response?.request_id ?? ''
      if (response?.success) {
        return response.data ?? null
      }
      if (response && typeof response === 'object' && 'success' in response) {
        errorMock.value = options.errorMsg ?? response.message ?? '操作失败'
        return null
      }
      return null
    },
  }),
}))

vi.mock('@/composables/useBackendReadiness', () => ({
  useBackendReadiness: () => ({
    readinessState: 'ready',
    readinessMessage: '后端已就绪',
    requestId: 'req-ready-1',
    backendReady: true,
    usingMockFallback: false,
    checkBackendReadiness: vi.fn().mockResolvedValue({
      ready: true,
      backendReady: true,
      usingMockFallback: false,
      message: '后端已就绪',
      requestId: 'req-ready-1',
    }),
  }),
}))

vi.mock('@/stores/apiStores', () => ({
  useTradingSignalsStore: () => ({
    loading: false,
    error: null,
    lastFetch: null,
    requestCount: 0,
    lastDurationMs: null,
    averageDurationMs: null,
    refresh: vi.fn().mockResolvedValue(undefined),
  }),
  useRiskAlertsStore: () => ({
    loading: false,
    error: null,
    lastFetch: null,
    requestCount: 0,
    lastDurationMs: null,
    averageDurationMs: null,
    refresh: vi.fn().mockResolvedValue(undefined),
  }),
  useWatchlistsStore: () => ({
    loading: false,
    error: null,
    lastFetch: null,
    requestCount: 0,
    lastDurationMs: null,
    averageDurationMs: null,
    refresh: vi.fn().mockResolvedValue(undefined),
  }),
  useTechnicalIndicatorsStore: () => ({
    loading: false,
    error: null,
    lastFetch: null,
    requestCount: 0,
    lastDurationMs: null,
    averageDurationMs: null,
    refresh: vi.fn().mockResolvedValue(undefined),
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      template: '<button @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
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

import SystemApiPage from '../API.vue'

describe('SystemApi routed trace truth', () => {
  beforeEach(() => {
    errorMock.value = null
    loadingMock.value = false
    lastRequestIdMock.value = ''
    localStorage.clear()
    getSystemHealthMock.mockReset().mockResolvedValue({
      success: true,
      data: {
        status: 'healthy',
        service: 'mystocks-backend',
        version: '2.0.0',
      },
      request_id: 'req-health-real',
    })
    getDetailedSystemHealthMock.mockReset().mockResolvedValue({
      success: true,
      data: {
        status: 'healthy',
        output: 'detailed health payload',
      },
      request_id: 'req-health-detailed',
    })
  })

  it('shows the traced request id from useArtDecoApi instead of fabricating a local sys id', async () => {
    const wrapper = mount(SystemApiPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('REQ_ID: req-health-real')
    expect(wrapper.text()).not.toMatch(/REQ_ID:\s*sys-\d+/)
  })

  it('does not present middleware rows as active runtime facts when the health probe failed', async () => {
    errorMock.value = '无法连接到后端服务'
    lastRequestIdMock.value = 'req-health-fail'
    getSystemHealthMock.mockResolvedValueOnce({
      success: false,
      message: 'health failed',
      request_id: 'req-health-fail',
    })

    const wrapper = mount(SystemApiPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('无法连接到后端服务，当前暂无已验证系统探针快照。')
    expect(wrapper.text()).not.toContain('性能追踪启用')
    expect(wrapper.text()).not.toContain('统一响应启用')
    expect(wrapper.text()).not.toContain('Redis 缓存活跃')
    expect(wrapper.text()).toContain('性能追踪未校验')
    expect(wrapper.text()).toContain('统一响应未校验')
    expect(wrapper.text()).toContain('Redis 缓存未校验')
  })

  it('suppresses fabricated delta chrome and pseudo precision for count-or-label KPI cards', async () => {
    const wrapper = mount(SystemApiPage as never, {
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
    expect(statValues).toEqual(['HEALTHY', 'mystocks-backend', '2.0.0', '3'])
    expect(statsStrip.text()).not.toContain('+0%')
    expect(statsStrip.text()).not.toContain('3.00')
    expect(statsStrip.text()).not.toContain('2.00')
  })

  it('keeps stat-strip labels unresolved while the first system probe snapshot is still pending', async () => {
    loadingMock.value = true
    getSystemHealthMock.mockReset().mockReturnValue(
      new Promise(() => {
        // Hold the first probe unresolved so the route stays in its pending shell.
      }),
    )

    const wrapper = mount(SystemApiPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    const statsStrip = wrapper.get('.stats-strip')
    const statValues = statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('STATUS: UNKNOWN')
    expect(statValues).toEqual(['UNKNOWN', '--', '--', '--'])
    expect(wrapper.get('.content-shell-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.content-shell-meta').text()).toContain('MIDDLEWARE: --')
  })

  it('accepts plain health probe payloads instead of collapsing 200 probes into unknown runtime state', async () => {
    errorMock.value = null
    lastRequestIdMock.value = 'req-health-plain'
    getSystemHealthMock.mockReset().mockResolvedValue({
      status: 'healthy',
      version: '1.0.0',
      timestamp: '2026-04-29T07:31:30.538Z',
    })

    const wrapper = mount(SystemApiPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    const statValues = wrapper.get('.stats-strip').findAll('.artdeco-stat-value').map((node) => node.text())

    expect(wrapper.text()).not.toContain('当前遥测面板可能仅显示静态说明。')
    expect(statValues).toEqual(['HEALTHY', 'N/A', '1.0.0', '3'])
  })

  it('does not leak a failed first-load request id before any verified system api snapshot exists', async () => {
    errorMock.value = '无法连接到后端服务'
    lastRequestIdMock.value = 'req-system-api-first-fail'
    getSystemHealthMock.mockReset().mockResolvedValue({
      success: false,
      message: 'health failed',
      request_id: 'req-system-api-first-fail',
    })

    const wrapper = mount(SystemApiPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-system-api-first-fail')
    expect(wrapper.get('.content-shell-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.text()).toContain('无法连接到后端服务，当前暂无已验证系统探针快照。')
    expect(wrapper.text()).not.toContain('当前遥测面板可能仅显示静态说明。')
  })

  it('keeps the last verified request id and visible health snapshot when a refresh fails', async () => {
    getSystemHealthMock.mockReset()
    getSystemHealthMock
      .mockResolvedValueOnce({
        success: true,
        data: {
          status: 'healthy',
          service: 'mystocks-backend',
          version: '2.0.0',
        },
        request_id: 'req-system-api-success',
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'refresh failed',
        request_id: 'req-system-api-refresh-fail',
      })

    const wrapper = mount(SystemApiPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()
    wrapper.vm.$forceUpdate()
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-system-api-success')
    expect(wrapper.text()).toContain('mystocks-backend')
    expect(wrapper.text()).toContain('2.0.0')

    errorMock.value = '无法连接到后端服务'
    lastRequestIdMock.value = 'req-system-api-refresh-fail'
    await wrapper.get('button').trigger('click')
    await flushPromises()
    wrapper.vm.$forceUpdate()
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-system-api-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('req-system-api-refresh-fail')
    expect(wrapper.get('.content-shell-meta').text()).toContain('REQ_ID: req-system-api-success')
    expect(wrapper.text()).toContain('无法连接到后端服务，当前仍显示上次成功同步的系统探针快照。')
    expect(wrapper.text()).toContain('mystocks-backend')
    expect(wrapper.text()).toContain('2.0.0')
  })
})
