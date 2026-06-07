import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const strategiesMock = ref([] as Array<Record<string, unknown>>)
const loadingMock = ref(false)
const errorMock = ref(null as string | null)
const dataSourceMock = ref('real')
const lastRequestIdMock = ref('req-strategy-repo')
const lastProcessTimeMsMock = ref('36.00')

const {
  createStrategyMock,
  deleteStrategyMock,
  fetchStrategiesMock,
  getSnapshotMock,
  pauseStrategyMock,
  removeSnapshotMock,
  resumeStrategyMock,
  routerPushMock,
  setActiveStrategyMock,
  setBacktestTaskSnapshotMock,
  setParametersSnapshotMock,
  setStatusSnapshotMock,
  startStrategyMock,
  stopStrategyMock,
  updateStrategyMock,
  upsertFromStrategyListMock,
} = vi.hoisted(() => ({
  createStrategyMock: vi.fn(),
  dataSourceMock: { value: 'real' },
  deleteStrategyMock: vi.fn(),
  errorMock: { value: null as string | null },
  fetchStrategiesMock: vi.fn(),
  getSnapshotMock: vi.fn(() => null),
  pauseStrategyMock: vi.fn(),
  removeSnapshotMock: vi.fn(),
  resumeStrategyMock: vi.fn(),
  routerPushMock: vi.fn(),
  setActiveStrategyMock: vi.fn(),
  setBacktestTaskSnapshotMock: vi.fn(),
  setParametersSnapshotMock: vi.fn(),
  setStatusSnapshotMock: vi.fn(),
  startStrategyMock: vi.fn(),
  stopStrategyMock: vi.fn(),
  updateStrategyMock: vi.fn(),
  upsertFromStrategyListMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPushMock,
  }),
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  },
}))

vi.mock('@/composables/useStrategy', () => ({
  useStrategy: () => ({
    strategies: strategiesMock,
    loading: loadingMock,
    error: errorMock,
    dataSource: dataSourceMock,
    lastRequestId: lastRequestIdMock,
    lastProcessTimeMs: lastProcessTimeMsMock,
    fetchStrategies: fetchStrategiesMock,
    startStrategy: startStrategyMock,
    stopStrategy: stopStrategyMock,
    pauseStrategy: pauseStrategyMock,
    resumeStrategy: resumeStrategyMock,
    createStrategy: createStrategyMock,
    updateStrategy: updateStrategyMock,
    deleteStrategy: deleteStrategyMock,
  }),
}))

vi.mock('@/composables/strategy/useStrategyCrossTabContext', () => ({
  useStrategyCrossTabContext: () => ({
    upsertFromStrategyList: upsertFromStrategyListMock,
    setParametersSnapshot: setParametersSnapshotMock,
    setStatusSnapshot: setStatusSnapshotMock,
    setBacktestTaskSnapshot: setBacktestTaskSnapshotMock,
    removeSnapshot: removeSnapshotMock,
    setActiveStrategy: setActiveStrategyMock,
    getSnapshot: getSnapshotMock,
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

import ArtDecoStrategyManagement from '../ArtDecoStrategyManagement.vue'

function createStrategyRows() {
  return [
    {
      id: '101',
      code: 'momentum-alpha',
      name: 'Momentum Alpha',
      type: 'momentum',
      status: 'running',
      lastRunTime: '2026-04-03T09:30:00Z',
      nextRunTime: '-',
      totalReturn: '-',
      sharpeRatio: '-',
      maxDrawdown: '-',
      winRate: '-',
      description: 'northbound momentum',
    },
    {
      id: '102',
      code: 'reversion-beta',
      name: 'Reversion Beta',
      type: 'mean_reversion',
      status: 'paused',
      lastRunTime: '2026-04-03T09:45:00Z',
      nextRunTime: '-',
      totalReturn: '-',
      sharpeRatio: '-',
      maxDrawdown: '-',
      winRate: '-',
      description: 'pullback re-entry',
    },
  ]
}

function mountPage() {
  return mount(ArtDecoStrategyManagement as never, {
    global: {
      directives: {
        loading: {},
      },
    },
  })
}

describe('ArtDecoStrategyManagement routed summary truth', () => {
  beforeEach(() => {
    strategiesMock.value = createStrategyRows()
    loadingMock.value = false
    errorMock.value = null
    dataSourceMock.value = 'real'
    lastRequestIdMock.value = 'req-strategy-repo'
    lastProcessTimeMsMock.value = '36.00'
    fetchStrategiesMock.mockReset()
    startStrategyMock.mockReset()
    stopStrategyMock.mockReset()
    pauseStrategyMock.mockReset()
    resumeStrategyMock.mockReset()
    createStrategyMock.mockReset()
    updateStrategyMock.mockReset()
    deleteStrategyMock.mockReset()
    upsertFromStrategyListMock.mockReset()
    setParametersSnapshotMock.mockReset()
    setStatusSnapshotMock.mockReset()
    setBacktestTaskSnapshotMock.mockReset()
    removeSnapshotMock.mockReset()
    setActiveStrategyMock.mockReset()
    getSnapshotMock.mockReset().mockReturnValue(null)
    routerPushMock.mockReset()
  })

  it('does not render verified repository tallies as precise-decimal delta stats when the route only provides counts', async () => {
    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual([
      '2',
      '1',
      '0',
      '全部状态',
    ])
    expect(wrapper.find('.content-shell-meta').text()).toContain('MATCHED: 2')
    expect(wrapper.find('.content-shell-meta').text()).toContain('PAGE: 1 / 1')
    expect(wrapper.find('.header-meta').text()).toContain('MATCHED: 2')
    expect(wrapper.find('.header-meta').text()).toContain('PAGE: 1 / 1')
    expect(wrapper.find('.stats-strip').text()).not.toContain('2.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('1.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('0.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('+0%')
  })

  it('keeps first-load repository tallies and sibling meta in pending placeholders instead of fabricated zeros or false empty-state copy', async () => {
    strategiesMock.value = []
    loadingMock.value = true

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual([
      '--',
      '--',
      '--',
      '全部状态',
    ])
    expect(wrapper.find('.content-shell-meta').text()).toContain('MATCHED: --')
    expect(wrapper.find('.content-shell-meta').text()).toContain('PAGE: -- / --')
    expect(wrapper.find('.header-meta').text()).toContain('MATCHED: --')
    expect(wrapper.find('.header-meta').text()).toContain('PAGE: -- / --')
    expect(wrapper.text()).toContain('策略仓库同步中，正在等待真实策略返回。')
    expect(wrapper.text()).not.toContain('REAL 数据为空，请先创建策略。')
    expect(wrapper.find('.stats-strip').text()).not.toContain('0.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('+0%')
  })

  it('does not present failed first-load repository tallies as faux zero metrics', async () => {
    strategiesMock.value = []
    errorMock.value = 'strategy registry unavailable'

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.findAll('.stats-strip .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual([
      '--',
      '--',
      '--',
      '全部状态',
    ])
    expect(wrapper.find('.content-shell-meta').text()).toContain('MATCHED: --')
    expect(wrapper.find('.content-shell-meta').text()).toContain('PAGE: -- / --')
    expect(wrapper.text()).toContain('REAL 请求失败，请稍后重试。')
    expect(wrapper.find('.stats-strip').text()).not.toContain('0.00')
    expect(wrapper.find('.stats-strip').text()).not.toContain('+0%')
  })

  it('does not leak failed first-load repository request metadata before any verified snapshot exists', async () => {
    strategiesMock.value = []
    errorMock.value = 'strategy registry unavailable'
    lastRequestIdMock.value = 'req-strategy-repo-first-fail'
    lastProcessTimeMsMock.value = '77'

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: N/A ms')
    expect(wrapper.find('.hero-meta').text()).not.toContain('req-strategy-repo-first-fail')
    expect(wrapper.find('.hero-meta').text()).not.toContain('77')
    expect(wrapper.text()).not.toContain('req-strategy-repo-first-fail')
  })

  it('keeps the last verified repository request metadata and visible rows when a manual refresh fails', async () => {
    let fetchCount = 0
    fetchStrategiesMock.mockImplementation(async () => {
      fetchCount += 1

      if (fetchCount === 1) {
        errorMock.value = 'strategy repository refresh unavailable'
        lastRequestIdMock.value = 'req-strategy-repo-refresh-fail'
        lastProcessTimeMsMock.value = '88'
        dataSourceMock.value = 'real-offline'
        return strategiesMock.value
      }

      return strategiesMock.value
    })

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-repo')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: 36.00 ms')
    expect(wrapper.findAll('.strategy-table tbody tr')).toHaveLength(2)

    const refreshButton = wrapper
      .findAll('button')
      .find((node) => node.text().includes('刷新仓库'))

    expect(refreshButton).toBeTruthy()
    await refreshButton!.trigger('click')
    await flushPromises()

    expect(fetchStrategiesMock).toHaveBeenCalledTimes(1)

    expect(wrapper.find('.hero-meta').text()).toContain('REQ_ID: req-strategy-repo')
    expect(wrapper.find('.hero-meta').text()).toContain('PROCESS: 36.00 ms')
    expect(wrapper.find('.hero-meta').text()).not.toContain('req-strategy-repo-refresh-fail')
    expect(wrapper.text()).toContain('strategy repository refresh unavailable')
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的策略仓库快照')
    expect(wrapper.findAll('.strategy-table tbody tr')).toHaveLength(2)
    expect(wrapper.find('.strategy-table').text()).toContain('Momentum Alpha')
  })
})
