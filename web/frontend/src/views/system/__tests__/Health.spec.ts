import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  errorMock,
  getHealthMock,
  loadingMock,
  lastRequestIdMock,
} = vi.hoisted(() => ({
  errorMock: { value: null as string | null, __v_isRef: true },
  getHealthMock: vi.fn(),
  loadingMock: { value: false, __v_isRef: true },
  lastRequestIdMock: { value: '', __v_isRef: true },
}))

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: getHealthMock,
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

import SystemHealthPage from '../Health.vue'

describe('SystemHealth routed runtime truth', () => {
  beforeEach(() => {
    errorMock.value = '无法连接到后端服务'
    loadingMock.value = false
    lastRequestIdMock.value = ''
    getHealthMock.mockReset().mockResolvedValue({
      success: false,
      message: 'health failed',
      request_id: 'req-health-fail',
    })
  })

  it('does not present middleware rows as enabled runtime facts when the health probe failed', async () => {
    const wrapper = mount(SystemHealthPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('无法连接到后端服务，当前仅展示健康矩阵壳层。')
    expect(wrapper.text()).not.toContain('Performance TracingENABLED')
    expect(wrapper.text()).not.toContain('Unified ResponseENABLED')
    expect(wrapper.text()).not.toContain('Redis CachingACTIVE')
    expect(wrapper.text()).toContain('Performance TracingUNVERIFIED')
    expect(wrapper.text()).toContain('Unified ResponseUNVERIFIED')
    expect(wrapper.text()).toContain('Redis CachingUNVERIFIED')
  })

  it('does not expose a failed request id before any verified health snapshot exists', async () => {
    getHealthMock.mockResolvedValueOnce({
      success: false,
      message: 'health failed',
      request_id: 'req-health-first-fail',
    })

    const wrapper = mount(SystemHealthPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()
    wrapper.vm.$forceUpdate()
    await flushPromises()

    expect(wrapper.text()).toContain('REQ_ID: N/A')
    expect(wrapper.text()).not.toContain('req-health-first-fail')
  })

  it('keeps stat-strip labels unresolved while the first health snapshot is still pending', async () => {
    errorMock.value = null
    loadingMock.value = true
    getHealthMock.mockReset().mockReturnValue(
      new Promise(() => {
        // Keep the initial probe unresolved so the route stays in its first-load shell.
      }),
    )

    const wrapper = mount(SystemHealthPage as never, {
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
    expect(wrapper.get('.content-shell-meta').text()).toContain('STATUS: UNKNOWN')
    expect(wrapper.get('.content-shell-meta').text()).toContain('MIDDLEWARE: --')
  })

  it('keeps the last verified request id when a refresh fails after a successful snapshot', async () => {
    errorMock.value = null
    getHealthMock.mockReset()
      .mockResolvedValueOnce({
        success: true,
        request_id: 'req-health-success',
        data: {
          status: 'healthy',
          service: 'mystocks-backend',
          version: '2.0.0',
        },
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'health failed',
        request_id: 'req-health-refresh-fail',
      })

    const wrapper = mount(SystemHealthPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()
    wrapper.vm.$forceUpdate()
    await flushPromises()
    expect(wrapper.text()).toContain('REQ_ID: req-health-success')

    await wrapper.get('button').trigger('click')
    await flushPromises()
    wrapper.vm.$forceUpdate()
    await flushPromises()

    expect(wrapper.text()).toContain('REQ_ID: req-health-success')
    expect(wrapper.text()).not.toContain('REQ_ID: req-health-refresh-fail')
    expect(wrapper.text()).toContain('mystocks-backend')
    expect(getHealthMock.mock.calls.length).toBeGreaterThanOrEqual(2)
  })

  it('suppresses fabricated delta chrome and pseudo precision for count-or-label KPI cards', async () => {
    errorMock.value = null
    getHealthMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'req-health-ok',
      data: {
        status: 'healthy',
        service: 'mystocks-backend',
        version: '2.0.0',
      },
    })

    const wrapper = mount(SystemHealthPage as never, {
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

  it('accepts plain health probe payloads instead of collapsing 200 probes into unknown runtime state', async () => {
    errorMock.value = null
    getHealthMock.mockReset().mockResolvedValue({
      status: 'healthy',
      version: '1.0.0',
      timestamp: '2026-04-29T07:31:30.538Z',
    })

    const wrapper = mount(SystemHealthPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    const statValues = wrapper.get('.stats-strip').findAll('.artdeco-stat-value').map((node) => node.text())

    expect(wrapper.text()).not.toContain('当前仅展示健康矩阵壳层。')
    expect(statValues).toEqual(['HEALTHY', 'N/A', '1.0.0', '3'])
  })
})
