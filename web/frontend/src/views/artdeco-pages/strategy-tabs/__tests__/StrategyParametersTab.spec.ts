import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  errorMock,
  getSnapshotMock,
  getStrategiesMock,
  lastProcessTimeMock,
  lastRequestIdMock,
  loadingMock,
  pushMock,
  routeMock,
  setActiveStrategyMock,
} = vi.hoisted(() => ({
  errorMock: require('vue').ref(null as string | null),
  getSnapshotMock: vi.fn(() => null),
  getStrategiesMock: vi.fn(),
  lastProcessTimeMock: require('vue').ref('0'),
  lastRequestIdMock: require('vue').ref(''),
  loadingMock: require('vue').ref(false),
  pushMock: vi.fn(),
  routeMock: require('vue').reactive({
    query: {} as Record<string, unknown>,
  }),
  setActiveStrategyMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
  useRouter: () => ({
    push: pushMock,
  }),
}))

vi.mock('@/api', () => ({
  strategyApi: {
    getStrategies: getStrategiesMock,
  },
}))

vi.mock('@/composables/strategy/useStrategyCrossTabContext', () => ({
  useStrategyCrossTabContext: () => ({
    getSnapshot: getSnapshotMock,
    setActiveStrategy: setActiveStrategyMock,
  }),
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: errorMock,
    lastRequestId: lastRequestIdMock,
    lastProcessTime: lastProcessTimeMock,
    exec: async (apiCall: () => Promise<unknown>) => {
      loadingMock.value = true

      try {
        const response = await apiCall()

        if (response && typeof response === 'object' && 'request_id' in response) {
          lastRequestIdMock.value = String((response as { request_id?: unknown }).request_id ?? '')
        }

        if (response && typeof response === 'object' && 'process_time_ms' in response) {
          lastProcessTimeMock.value = String((response as { process_time_ms?: unknown }).process_time_ms ?? '')
        }

        if (response && typeof response === 'object' && 'success' in response && (response as { success: boolean }).success === false) {
          errorMock.value =
            (response as { message?: unknown }).message && String((response as { message?: unknown }).message)
              ? String((response as { message?: unknown }).message)
              : '获取策略参数失败'
          return null
        }

        errorMock.value = null
        return (response as { data?: unknown })?.data ?? response
      } catch (requestError: unknown) {
        errorMock.value = requestError instanceof Error ? requestError.message : '获取策略参数失败'
        return null
      } finally {
        loadingMock.value = false
      }
    },
  }),
}))

import StrategyParametersTab from '../StrategyParametersTab.vue'

function mountStrategyParametersTab() {
  return mount(StrategyParametersTab as never, {
    global: {
      stubs: {
        ArtDecoBadge: {
          props: ['text'],
          template: '<span class="artdeco-badge-stub">{{ text }}</span>',
        },
        ArtDecoButton: {
          emits: ['click'],
          template: '<button @click="$emit(\'click\', $event)"><slot /><slot name="icon" /></button>',
        },
        ArtDecoHeader: {
          props: ['title', 'subtitle', 'statusText'],
          template: '<div><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></div>',
        },
        ArtDecoIcon: {
          template: '<span class="artdeco-icon-stub" />',
        },
        ArtDecoStatCard: {
          props: ['label', 'showChange', 'value'],
          template: `
            <div class="artdeco-stat-card-stub">
              <span class="artdeco-stat-label">{{ label }}</span>
              <span class="artdeco-stat-value">{{ typeof value === 'number' ? value.toFixed(2) : value }}</span>
              <span v-if="showChange !== false" class="artdeco-stat-change">+0%</span>
            </div>
          `,
        },
      },
      directives: {
        loading: {},
      },
    },
  })
}

function createStrategiesPayload() {
  return {
    success: true,
    request_id: 'req-strategy-parameters-success',
    process_time_ms: 12.5,
    data: [
      {
        strategy_id: 101,
        strategy_name: 'Momentum Alpha',
        description: 'northbound momentum',
        status: 'active',
        parameters: [
          { name: 'lookback', value: 20, data_type: 'number' },
          { name: 'risk_limit', value: 0.05, data_type: 'number' },
        ],
      },
      {
        strategy_id: 102,
        strategy_name: 'Reversion Beta',
        description: 'pullback re-entry',
        status: 'paused',
        parameters: [
          { name: 'z_score', value: 2.1, data_type: 'number' },
        ],
      },
    ],
  }
}

describe('StrategyParametersTab', () => {
  beforeEach(() => {
    errorMock.value = null
    getSnapshotMock.mockReset().mockReturnValue(null)
    getStrategiesMock.mockReset()
    lastProcessTimeMock.value = '0'
    lastRequestIdMock.value = ''
    loadingMock.value = false
    pushMock.mockReset()
    setActiveStrategyMock.mockReset()
    routeMock.query = { strategyId: '101' }
  })

  it('does not present verified parameter tallies as faux delta metrics or decimal pseudo precision', async () => {
    getStrategiesMock.mockResolvedValue(createStrategiesPayload())

    const wrapper = mountStrategyParametersTab()

    await flushPromises()

    const statValues = wrapper.findAll('.artdeco-stat-value').map((node) => node.text())

    expect(statValues).toEqual(['1', '2', '0', '101'])
    expect(wrapper.findAll('.artdeco-stat-change')).toHaveLength(0)
  })

  it('does not present failed first-load parameter tallies as faux zero metrics', async () => {
    getStrategiesMock.mockResolvedValue({
      success: false,
      message: 'registry unavailable',
      request_id: 'req-strategy-parameters-first-fail',
      process_time_ms: 48.5,
    })

    const wrapper = mountStrategyParametersTab()

    await flushPromises()

    const statValues = wrapper.findAll('.artdeco-stat-value').map((node) => node.text())

    expect(wrapper.text()).toContain('策略参数加载失败')
    expect(statValues).toEqual(['--', '--', '--', '101'])
    expect(wrapper.findAll('.artdeco-stat-change')).toHaveLength(0)
  })

  it('does not leak failed first-load parameter request metadata before any verified snapshot exists', async () => {
    getStrategiesMock.mockResolvedValue({
      success: false,
      message: 'registry unavailable',
      request_id: 'req-strategy-parameters-first-fail',
      process_time_ms: 48.5,
    })

    const wrapper = mountStrategyParametersTab()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: N/A ms')
    expect(wrapper.text()).not.toContain('req-strategy-parameters-first-fail')
    expect(wrapper.text()).not.toContain('48.50')
  })

  it('keeps the last verified parameter request metadata and visible cards when a manual refresh fails', async () => {
    getStrategiesMock
      .mockResolvedValueOnce(createStrategiesPayload())
      .mockResolvedValueOnce({
        success: false,
        message: '获取策略参数失败',
        request_id: 'req-strategy-parameters-refresh-fail',
        process_time_ms: 77.7,
      })

    const wrapper = mountStrategyParametersTab()

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-parameters-success')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: 12.50 ms')
    expect(wrapper.find('.hero-meta').text()).not.toContain('req-strategy-parameters-refresh-fail')
    expect(wrapper.find('.hero-meta').text()).not.toContain('77.70')
    expect(wrapper.text()).toContain('获取策略参数失败')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的参数快照')
    expect(wrapper.findAll('.strategy-card')).toHaveLength(1)
    expect(wrapper.text()).toContain('Momentum Alpha')
  })

  it('does not leak the previous strategy parameter snapshot into a new route query without its own verified context', async () => {
    getStrategiesMock.mockResolvedValue(createStrategiesPayload())

    const wrapper = mountStrategyParametersTab()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-parameters-success')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: 12.50 ms')
    expect(wrapper.findAll('.strategy-card')).toHaveLength(1)
    expect(wrapper.text()).toContain('Momentum Alpha')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('FOCUS: 202')
    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: N/A ms')
    expect(wrapper.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '202'])
    expect(wrapper.findAll('.strategy-card')).toHaveLength(0)
    expect(wrapper.text()).toContain('未找到策略 202 的参数配置')
    expect(wrapper.text()).not.toContain('Momentum Alpha')
  })
})
