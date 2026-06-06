import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getSystemResourcesMock,
  errorMock,
  lastRequestIdMock,
} = vi.hoisted(() => ({
  getSystemResourcesMock: vi.fn(),
  errorMock: { value: null as string | null },
  lastRequestIdMock: { value: '' },
}))

vi.mock('@/api/index', () => ({
  monitoringApi: {
    getSystemResources: getSystemResourcesMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: { value: false },
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    exec: async (
      apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string }>,
      options: { errorMsg?: string } = {},
    ) => {
      errorMock.value = null
      const response = await apiCall()
      lastRequestIdMock.value = response?.request_id ?? ''
      if (response?.success) {
        return response.data ?? null
      }
      errorMock.value = options.errorMsg ?? response?.message ?? '操作失败'
      return null
    },
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoBadge: {
      props: ['text'],
      template: '<span class="badge">{{ text }}</span>',
    },
    ArtDecoButton: {
      emits: ['click'],
      template: '<button v-bind="$attrs" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      template: '<div><slot /><slot name="title" /></div>',
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

import ResourcesPage from '../Resources.vue'

const buildPayload = () => ({
  success: true,
  request_id: 'req-system-resources',
  data: {
    node: {
      node_id: 'local-runtime',
      scope: 'single-node',
      sampled_at: '2026-05-07T00:00:00+00:00',
      window_minutes: 60,
      polling_interval_seconds: 15,
      overall_status: 'warning',
    },
    host: {
      cpu: {
        metric_key: 'cpu_percent',
        label: 'CPU',
        unit: '%',
        current_value: 82.5,
        status: 'warning',
        warning_threshold: 70,
        critical_threshold: 90,
        series: [
          { timestamp: '2026-05-06T23:59:45+00:00', value: 80.0 },
          { timestamp: '2026-05-07T00:00:00+00:00', value: 82.5 },
        ],
        meta: {},
      },
      memory: {
        metric_key: 'memory_percent',
        label: '内存',
        unit: '%',
        current_value: 64.2,
        status: 'normal',
        warning_threshold: 75,
        critical_threshold: 90,
        series: [{ timestamp: '2026-05-07T00:00:00+00:00', value: 64.2 }],
        meta: {},
      },
      disk: {
        metric_key: 'disk_percent',
        label: '磁盘',
        unit: '%',
        current_value: 91.2,
        status: 'critical',
        warning_threshold: 80,
        critical_threshold: 90,
        series: [{ timestamp: '2026-05-07T00:00:00+00:00', value: 91.2 }],
        meta: {},
      },
      load: {
        metric_key: 'load_percent',
        label: '负载',
        unit: '%',
        current_value: 24.0,
        status: 'normal',
        warning_threshold: 70,
        critical_threshold: 90,
        series: [{ timestamp: '2026-05-07T00:00:00+00:00', value: 24.0 }],
        meta: {},
      },
    },
    processes: [
      {
        process_key: 'mystocks-backend',
        display_name: 'mystocks-backend',
        status: 'normal',
        pid: 1234,
        cpu_percent: 12.4,
        memory_mb: 512.0,
        memory_percent: 5.0,
        sampled_at: '2026-05-07T00:00:00+00:00',
        started_at: '2026-05-06T23:00:00+00:00',
        thresholds: {},
        summary: 'cpu=12.4% memory=5.0%',
      },
    ],
    dependencies: [
      {
        dependency_key: 'postgresql',
        display_name: 'PostgreSQL',
        status: 'normal',
        summary: 'pool healthy',
        sampled_at: '2026-05-07T00:00:00+00:00',
        warning_threshold: 70,
        critical_threshold: 90,
        metrics: { active_connections: 2, usage_percentage: 20.0 },
      },
    ],
    thresholds: {
      'host.cpu_percent': { warning: 70, critical: 90, unit: '%' },
    },
  },
})

describe('System resources page', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    errorMock.value = null
    lastRequestIdMock.value = ''
    getSystemResourcesMock.mockReset().mockResolvedValue(buildPayload())
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders snapshot cards, dependency/process sections, and threshold states from the unified resource contract', async () => {
    const wrapper = mount(ResourcesPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('资源使用工作台')
    expect(wrapper.text()).toContain('CPU')
    expect(wrapper.text()).toContain('82.5%')
    expect(wrapper.text()).toContain('WARNING')
    expect(wrapper.text()).toContain('CRITICAL')
    expect(wrapper.text()).toContain('mystocks-backend')
    expect(wrapper.text()).toContain('PostgreSQL')
    expect(wrapper.findAll('svg.sparkline')).not.toHaveLength(0)
  })

  it('polls every 15 seconds and supports pause / resume controls', async () => {
    const wrapper = mount(ResourcesPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()
    expect(getSystemResourcesMock).toHaveBeenCalledTimes(1)

    await vi.advanceTimersByTimeAsync(15000)
    await flushPromises()
    expect(getSystemResourcesMock).toHaveBeenCalledTimes(2)

    await wrapper.get('button.polling-toggle').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('恢复轮询')
    await vi.advanceTimersByTimeAsync(15000)
    await flushPromises()
    expect(getSystemResourcesMock).toHaveBeenCalledTimes(2)

    await wrapper.get('button.polling-toggle').trigger('click')
    await flushPromises()
    await vi.advanceTimersByTimeAsync(15000)
    await flushPromises()
    expect(getSystemResourcesMock).toHaveBeenCalledTimes(3)
  })

  it('keeps stats-strip counts unresolved while the first resource snapshot is still pending', async () => {
    let resolvePayload: ((value: ReturnType<typeof buildPayload>) => void) | null = null
    getSystemResourcesMock.mockReset().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePayload = resolve
        }),
    )

    const wrapper = mount(ResourcesPage as never, {
      global: {
        directives: {
          loading: {},
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('资源使用工作台')
    expect(wrapper.text()).toContain('REQ_ID: N/A')
    expect(wrapper.text()).toContain('STATUS: UNKNOWN')
    expect(wrapper.text()).toContain('NODE: --')
    expect(wrapper.text()).toContain('整体状态')
    expect(wrapper.text()).toContain('UNKNOWN')
    expect(wrapper.text()).toContain('监控节点')
    expect(wrapper.text()).toContain('N/A')
    expect(wrapper.text()).toContain('运行进程')
    expect(wrapper.text()).not.toContain('运行进程0')
    expect(wrapper.text()).toContain('关键告警')
    expect(wrapper.text()).not.toContain('关键告警0')
    expect(wrapper.text()).toContain('依赖摘要')
    expect(wrapper.text()).not.toContain('依赖摘要0')

    expect(wrapper.findAllComponents({ name: 'ArtDecoStatCard' }).map((card) => card.text())).toEqual([
      expect.stringContaining('整体状态UNKNOWN'),
      expect.stringContaining('监控节点--'),
      expect.stringContaining('运行进程--'),
      expect.stringContaining('关键告警--'),
      expect.stringContaining('依赖摘要--'),
    ])

    resolvePayload?.(buildPayload())
    await flushPromises()

    expect(wrapper.findAllComponents({ name: 'ArtDecoStatCard' }).map((card) => card.text())).toEqual([
      expect.stringContaining('整体状态WARNING'),
      expect.stringContaining('监控节点local-runtime'),
      expect.stringContaining('运行进程1'),
      expect.stringContaining('关键告警1'),
      expect.stringContaining('依赖摘要1'),
    ])
  })
})
