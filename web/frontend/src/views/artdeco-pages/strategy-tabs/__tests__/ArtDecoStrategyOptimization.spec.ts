import { flushPromises, mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  getStrategiesMock,
  routeMock,
  routerPushMock,
  getSnapshotMock,
  setActiveStrategyMock,
  setParametersSnapshotMock,
  setOptimizationSnapshotMock,
  messageSuccessMock,
  messageWarningMock,
} = vi.hoisted(() => ({
  getStrategiesMock: vi.fn(),
  routeMock: require('vue').reactive({
    query: { strategyId: '101' } as Record<string, unknown>,
  }),
  routerPushMock: vi.fn(),
  getSnapshotMock: vi.fn(() => null),
  setActiveStrategyMock: vi.fn(),
  setParametersSnapshotMock: vi.fn(),
  setOptimizationSnapshotMock: vi.fn(),
  messageSuccessMock: vi.fn(),
  messageWarningMock: vi.fn(),
}))

const snapshotsRef = ref<Record<string, unknown>>({})

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
  useRouter: () => ({
    push: routerPushMock,
  }),
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: messageSuccessMock,
    warning: messageWarningMock,
  },
}))

vi.mock('@/api', () => ({
  strategyApi: {
    getStrategies: getStrategiesMock,
  },
}))

vi.mock('@/composables/strategy/useStrategyCrossTabContext', () => ({
  useStrategyCrossTabContext: () => ({
    snapshots: snapshotsRef,
    getSnapshot: getSnapshotMock,
    setActiveStrategy: setActiveStrategyMock,
    setParametersSnapshot: setParametersSnapshotMock,
    setOptimizationSnapshot: setOptimizationSnapshotMock,
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoBadge: {
      props: ['text'],
      template: '<span class="artdeco-badge-stub">{{ text }}</span>',
    },
    ArtDecoButton: {
      props: ['disabled', 'loading'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      template: '<section class="artdeco-card-stub"><header><slot name="header" /></header><div><slot /></div></section>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<div><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></div>',
    },
    ArtDecoIcon: {
      template: '<span class="artdeco-icon-stub" />',
    },
    ArtDecoStatCard,
  }
})

import ArtDecoStrategyOptimization from '../ArtDecoStrategyOptimization.vue'

function createUnifiedResponse(data: unknown, requestId = 'req-strategy-opt'): Record<string, unknown> {
  return {
    success: true,
    code: 200,
    message: 'ok',
    data,
    request_id: requestId,
    process_time: '42ms',
    timestamp: '2026-04-30T00:00:00Z',
  }
}

function mountPage() {
  return mount(ArtDecoStrategyOptimization as never, {
    global: {
      directives: {
        loading: {},
      },
    },
  })
}

describe('ArtDecoStrategyOptimization routed summary truth', () => {
  beforeEach(() => {
    getStrategiesMock.mockReset().mockResolvedValue(createUnifiedResponse([
      {
        strategy_id: 101,
        strategy_name: 'Momentum Alpha',
        strategy_type: 'momentum',
        description: 'northbound momentum',
        status: 'active',
        updated_at: '2026-04-03T09:30:00Z',
        parameters: [
          { name: 'lookback', value: 20, data_type: 'number' },
          { name: 'risk_limit', value: 0.05, data_type: 'number' },
        ],
      },
      {
        strategy_id: 102,
        strategy_name: 'Reversion Beta',
        strategy_type: 'mean_reversion',
        description: 'pullback re-entry',
        status: 'paused',
        updated_at: '2026-04-03T09:45:00Z',
        parameters: [
          { name: 'z_score', value: 2.1, data_type: 'number' },
        ],
      },
    ]))
    routerPushMock.mockReset()
    getSnapshotMock.mockReset().mockReturnValue(null)
    setActiveStrategyMock.mockReset()
    setParametersSnapshotMock.mockReset()
    setOptimizationSnapshotMock.mockReset()
    messageSuccessMock.mockReset()
    messageWarningMock.mockReset()
    snapshotsRef.value = {}
    routeMock.query = { strategyId: '101' }
  })

  it('does not render verified optimization tallies as precise-decimal delta stats when the route only provides counts', async () => {
    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.content-shell-meta').text()).toContain('VISIBLE: 1')
    expect(wrapper.find('.header-meta').text()).toContain('TOTAL: 2')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['2', '1', '0', 'ID 101'])
    expect(wrapper.find('.stats-strip').text()).not.toContain('2.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('1.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('0.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('+0%')
  })

  it('keeps first-load optimization tallies and sibling count meta in pending placeholders instead of fabricated zeros or false missing-state copy', async () => {
    getStrategiesMock.mockReset().mockImplementation(() => new Promise(() => {}))

    const wrapper = mountPage()
    await nextTick()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', 'ID 101'])
    expect(wrapper.find('.content-shell-meta').text()).toContain('可见: --')
    expect(wrapper.find('.header-meta').text()).toContain('TOTAL: --')
    expect(wrapper.text()).toContain('优化候选同步中，正在等待真实候选返回。')
    expect(wrapper.text()).not.toContain('未找到策略 101 的优化候选')
    expect(wrapper.find('.stats-strip').text()).not.toContain('0.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('+0%')
  })

  it('does not leak failed first-load optimization request metadata before any verified snapshot exists', async () => {
    getStrategiesMock.mockReset().mockResolvedValue({
      success: false,
      code: 500,
      message: 'strategy list unavailable',
      data: null,
      request_id: 'req-strategy-opt-first-fail',
      process_time: '77ms',
      timestamp: '2026-05-03T00:00:00Z',
    })

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: N/A')
    expect(wrapper.text()).not.toContain('req-strategy-opt-first-fail')
    expect(wrapper.text()).not.toContain('77.00')
  })

  it('keeps the last verified optimization request metadata and visible rows when a manual refresh fails', async () => {
    getStrategiesMock.mockReset()
      .mockResolvedValueOnce(createUnifiedResponse([
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          description: 'northbound momentum',
          status: 'active',
          updated_at: '2026-04-03T09:30:00Z',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
            { name: 'risk_limit', value: 0.05, data_type: 'number' },
          ],
        },
        {
          strategy_id: 102,
          strategy_name: 'Reversion Beta',
          strategy_type: 'mean_reversion',
          description: 'pullback re-entry',
          status: 'paused',
          updated_at: '2026-04-03T09:45:00Z',
          parameters: [
            { name: 'z_score', value: 2.1, data_type: 'number' },
          ],
        },
      ], 'req-strategy-opt-success'))
      .mockResolvedValueOnce({
        success: false,
        code: 500,
        message: 'strategy optimization refresh unavailable',
        data: null,
        request_id: 'req-strategy-opt-refresh-fail',
        process_time: '88ms',
        timestamp: '2026-05-03T00:00:00Z',
      })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-opt-success')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: 42.00')
    expect(wrapper.find('.hero-meta').text()).not.toContain('req-strategy-opt-refresh-fail')
    expect(wrapper.find('.hero-meta').text()).not.toContain('88.00')
    expect(wrapper.text()).toContain('strategy optimization refresh unavailable')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的优化候选快照')
    expect(wrapper.findAll('.optimization-table tbody tr')).toHaveLength(1)
    expect(wrapper.text()).toContain('Momentum Alpha')
  })

  it('does not leak the previous strategy optimization snapshot into a new route query without its own verified context', async () => {
    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-opt')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: 42.00')
    expect(wrapper.findAll('.optimization-table tbody tr')).toHaveLength(1)
    expect(wrapper.text()).toContain('Momentum Alpha')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.content-shell-meta').text()).toContain('FOCUS: ID 202')
    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: N/A')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', 'ID 202'])
    expect(wrapper.findAll('.optimization-table tbody tr')).toHaveLength(0)
    expect(wrapper.text()).toContain('未找到策略 202 的优化候选')
    expect(wrapper.text()).not.toContain('Momentum Alpha')
  })
})
