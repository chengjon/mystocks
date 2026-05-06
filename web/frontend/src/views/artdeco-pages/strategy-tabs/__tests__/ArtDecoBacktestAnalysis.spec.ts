import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  errorMock,
  getBacktestResultMock,
  getBacktestStatusMock,
  getSnapshotMock,
  getStrategiesMock,
  loadingMock,
  routeMock,
  routerReplaceMock,
  setActiveStrategyMock,
  setBacktestTaskSnapshotMock,
  startBacktestMock,
} = vi.hoisted(() => ({
  errorMock: require('vue').ref(null as string | null),
  getBacktestResultMock: vi.fn(),
  getBacktestStatusMock: vi.fn(),
  getSnapshotMock: vi.fn(() => null),
  getStrategiesMock: vi.fn(),
  loadingMock: require('vue').ref(false),
  routeMock: require('vue').reactive({
    query: {} as Record<string, unknown>,
  }),
  routerReplaceMock: vi.fn(),
  setActiveStrategyMock: vi.fn(),
  setBacktestTaskSnapshotMock: vi.fn(),
  startBacktestMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
  useRouter: () => ({
    replace: routerReplaceMock,
  }),
}))

vi.mock('@/api', () => ({
  strategyApi: {
    getStrategies: getStrategiesMock,
  },
}))

vi.mock('@/api/services/strategyService', () => ({
  StrategyApiService: class StrategyApiService {
    startBacktest = startBacktestMock
    getBacktestStatus = getBacktestStatusMock
    getBacktestResult = getBacktestResultMock
  },
}))

vi.mock('@/composables/strategy/useStrategyCrossTabContext', () => ({
  useStrategyCrossTabContext: () => ({
    getSnapshot: getSnapshotMock,
    setActiveStrategy: setActiveStrategyMock,
    setBacktestTaskSnapshot: setBacktestTaskSnapshotMock,
  }),
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: errorMock,
    exec: async (apiCall: () => Promise<unknown>) => {
      loadingMock.value = true

      try {
        const response = await apiCall()

        if (response && typeof response === 'object' && 'success' in response && (response as { success: boolean }).success === false) {
          errorMock.value =
            (response as { message?: unknown }).message && String((response as { message?: unknown }).message)
              ? String((response as { message?: unknown }).message)
              : '获取REAL策略数据失败，当前显示空态'
          return null
        }

        errorMock.value = null
        return (response as { data?: unknown })?.data ?? response
      } catch (requestError: unknown) {
        errorMock.value = requestError instanceof Error ? requestError.message : '获取REAL策略数据失败，当前显示空态'
        return null
      } finally {
        loadingMock.value = false
      }
    },
  }),
}))

vi.mock('@/components/artdeco', () => ({
  ArtDecoBadge: {
    props: ['text'],
    template: '<span class="artdeco-badge-stub">{{ text }}</span>',
  },
  ArtDecoButton: {
    props: ['disabled'],
    emits: ['click'],
    template: '<button :disabled="disabled" @click="$emit(\'click\', $event)"><slot /></button>',
  },
  ArtDecoCard: {
    template: '<section class="artdeco-card-stub"><slot /></section>',
  },
  ArtDecoInput: {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  ArtDecoSelect: {
    props: ['modelValue', 'options'],
    emits: ['update:modelValue'],
    template: `
      <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
        <option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option>
      </select>
    `,
  },
  ArtDecoTable: {
    props: ['columns', 'data'],
    template: `
      <div class="artdeco-table-stub">
        <div class="artdeco-table-count">{{ data.length }}</div>
        <div
          v-for="(row, index) in data"
          :key="index"
          class="artdeco-table-row"
        >
          {{ Object.values(row).join(' | ') }}
        </div>
      </div>
    `,
  },
}))

import ArtDecoBacktestAnalysis from '../ArtDecoBacktestAnalysis.vue'

function mountPage() {
  return mount(ArtDecoBacktestAnalysis as never, {
    global: {
      stubs: {
        BacktestHeader: {
          props: ['statusText', 'lastUpdated'],
          emits: ['reset', 'run'],
          template: `
            <section class="backtest-header-stub">
              <div class="header-meta">
                <span>STATUS: {{ statusText }}</span>
                <span>UPDATED: {{ lastUpdated }}</span>
              </div>
              <button @click="$emit('reset')">重置参数</button>
              <button @click="$emit('run')">启动回测</button>
            </section>
          `,
        },
        BacktestKpiGrid: {
          props: ['items'],
          template: `
            <section class="backtest-kpi-grid-stub">
              <div
                v-for="item in items"
                :key="item.label"
                class="backtest-kpi-item"
              >
                {{ item.label }}:{{ item.value }}
              </div>
            </section>
          `,
        },
        BacktestWorkbenchTabs: {
          props: ['activeTab', 'tabs', 'metaItems'],
          emits: ['update:activeTab'],
          template: `
            <section class="backtest-workbench-tabs-stub">
              <button class="switch-reports-tab" @click="$emit('update:activeTab', 'reports')">切换到报告中心</button>
              <button class="switch-tasks-tab" @click="$emit('update:activeTab', 'tasks')">切换到回测任务</button>
              <button class="switch-optimize-tab" @click="$emit('update:activeTab', 'optimize')">切换到参数优化</button>
              <slot />
            </section>
          `,
        },
      },
    },
  })
}

describe('ArtDecoBacktestAnalysis freshness truth', () => {
  beforeEach(() => {
    errorMock.value = null
    getBacktestResultMock.mockReset()
    getBacktestStatusMock.mockReset()
    getSnapshotMock.mockReset().mockReturnValue(null)
    getStrategiesMock.mockReset()
    loadingMock.value = false
    routeMock.query = {}
    routerReplaceMock.mockReset()
    setActiveStrategyMock.mockReset()
    setBacktestTaskSnapshotMock.mockReset()
    startBacktestMock.mockReset()
  })

  it('does not present a fabricated current freshness timestamp when the first strategy list load failed', async () => {
    getStrategiesMock.mockResolvedValue({
      success: false,
      message: '获取REAL策略数据失败，当前显示空态',
      request_id: 'req-backtest-first-fail',
      data: null,
    })

    const wrapper = mountPage()

    await flushPromises()

    expect(wrapper.find('.header-meta').text()).toContain('UPDATED: --')
    expect(wrapper.find('.state-banner').text()).toContain('获取REAL策略数据失败，当前显示空态')
    expect(wrapper.text()).toContain('回测上下文加载失败')
    expect(wrapper.text()).toContain('获取REAL策略数据失败，当前显示空态')
    expect(wrapper.text()).not.toContain('req-backtest-first-fail')
  })

  it('does not rewrite UPDATED with a local current timestamp when run was clicked without any verified strategy context', async () => {
    getStrategiesMock.mockResolvedValue({
      success: false,
      message: '获取REAL策略数据失败，当前显示空态',
      request_id: 'req-backtest-first-fail',
      data: null,
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()

    expect(wrapper.find('.header-meta').text()).toContain('UPDATED: --')
    expect(wrapper.find('.state-banner').text()).toContain('未绑定有效策略ID，无法启动真实回测。')
    expect(wrapper.text()).not.toContain('req-backtest-first-fail')
  })

  it('does not advance UPDATED while the backtest task is only queued and no verified result snapshot exists yet', async () => {
    vi.useFakeTimers()
    try {
      vi.setSystemTime(new Date('2026-05-05T01:00:00Z'))
      getStrategiesMock.mockResolvedValue({
        success: true,
        data: [
          {
            strategy_id: 101,
            strategy_name: 'Momentum Alpha',
            strategy_type: 'momentum',
            status: 'active',
            parameters: [
              { name: 'lookback', value: 20, data_type: 'number' },
            ],
          },
        ],
      })
      startBacktestMock.mockImplementation(
        () =>
          new Promise(() => {
            // Hold the transport open so the page stays in queued state with no verified result snapshot yet.
          }),
      )

      const wrapper = mountPage()

      await flushPromises()
      const verifiedFreshness = wrapper.find('.header-meta').text()
      vi.setSystemTime(new Date('2026-05-05T01:30:00Z'))
      await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
      await flushPromises()

      expect(wrapper.find('.header-meta').text()).toBe(verifiedFreshness)
      expect(wrapper.find('.state-banner').text()).toContain('回测任务已创建，进入排队')
    } finally {
      vi.useRealTimers()
    }
  })

  it('does not fabricate a local report generation timestamp when the synced backtest result omitted completion metadata', async () => {
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: {
        task_id: 'bt-unit-001',
        status: 'completed',
        message: '回测任务已完成',
      },
      request_id: 'req-backtest-run-success',
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        total_return: 0.186,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        performance: {
          max_drawdown: 0.064,
        },
      },
      request_id: 'req-backtest-result-success',
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()
    await wrapper.find('.switch-reports-tab').trigger('click')
    await flushPromises()

    expect(wrapper.find('.artdeco-table-row').text()).toContain('2025-01-01 ~ 2025-12-31')
    expect(wrapper.find('.artdeco-table-row').text()).toContain('+18.6%')
    expect(wrapper.find('.artdeco-table-row').text()).toContain('--')
  })

  it('does not leak the previous strategy-local generated snapshot hint into a new route query without its own verified context', async () => {
    routeMock.query = { strategyId: '101' }
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion',
          strategy_type: 'reversion',
          status: 'draft',
          parameters: [
            { name: 'threshold', value: 3, data_type: 'number' },
          ],
        },
      ],
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()

    const generateSnapshotButton = wrapper
      .findAll('button')
      .find((button) => button.text() === '生成上下文快照')
    expect(generateSnapshotButton).toBeDefined()

    await generateSnapshotButton!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('最近快照：')
    expect(wrapper.text()).toContain('参数 1 项')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 202')
    expect(wrapper.find('.state-banner').text()).not.toContain('已生成 Momentum Alpha 的上下文快照')
    expect(wrapper.find('.state-banner').text()).toContain('当前任务、KPI 与报告摘要仍基于策略列表派生')
    expect(wrapper.text()).not.toContain('最近快照：')
    expect(wrapper.text()).toContain('当前任务、KPI 与报告摘要来自策略列表派生视图')
  })

  it('does not leak the previous strategy report rows into a new route query without its own verified report context', async () => {
    routeMock.query = { strategyId: '101' }
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion',
          strategy_type: 'reversion',
          status: 'draft',
          parameters: [
            { name: 'threshold', value: 3, data_type: 'number' },
          ],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: {
        task_id: 'bt-unit-002',
        status: 'completed',
        message: '回测任务已完成',
      },
      request_id: 'req-backtest-run-success',
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        total_return: 0.186,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        completed_at: '2026-05-05T09:36:00Z',
        performance: {
          max_drawdown: 0.064,
        },
      },
      request_id: 'req-backtest-result-success',
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()
    await wrapper.find('.switch-reports-tab').trigger('click')
    await flushPromises()

    expect(wrapper.findAll('.artdeco-table-row')).toHaveLength(1)
    expect(wrapper.text()).toContain('Momentum Alpha')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 202')
    expect(wrapper.findAll('.artdeco-table-row')).toHaveLength(0)
    expect(wrapper.text()).not.toContain('Momentum Alpha')
  })

  it('does not leak the previous strategy execution progress into a new route query without its own verified task context', async () => {
    routeMock.query = { strategyId: '101' }
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion',
          strategy_type: 'reversion',
          status: 'draft',
          parameters: [
            { name: 'threshold', value: 3, data_type: 'number' },
          ],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: {
        task_id: 'bt-unit-003',
        status: 'completed',
        message: '回测任务已完成',
      },
      request_id: 'req-backtest-run-success',
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        total_return: 0.186,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        completed_at: '2026-05-05T09:36:00Z',
        performance: {
          max_drawdown: 0.064,
        },
      },
      request_id: 'req-backtest-result-success',
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()

    expect(wrapper.find('.progress-panel').text()).toContain('100%')
    expect(wrapper.find('.log-panel').text()).toContain('回测结果已同步到报告中心')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 202')
    expect(wrapper.find('.progress-panel').text()).not.toContain('100%')
    expect(wrapper.find('.progress-panel').text()).toContain('等待任务')
    expect(wrapper.find('.log-panel').text()).not.toContain('回测结果已同步到报告中心')
  })

  it('does not leak the previous strategy task rows into a new route query without its own verified task context', async () => {
    routeMock.query = { strategyId: '101' }
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion',
          strategy_type: 'reversion',
          status: 'draft',
          parameters: [
            { name: 'threshold', value: 3, data_type: 'number' },
          ],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: {
        task_id: 'bt-unit-004',
        status: 'completed',
        message: '回测任务已完成',
      },
      request_id: 'req-backtest-run-success',
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        total_return: 0.186,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        completed_at: '2026-05-05T09:36:00Z',
        performance: {
          max_drawdown: 0.064,
        },
      },
      request_id: 'req-backtest-result-success',
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()
    await wrapper.find('.switch-tasks-tab').trigger('click')
    await flushPromises()

    expect(wrapper.find('.task-list').text()).toContain('Momentum Alpha')
    expect(wrapper.find('.task-list').text()).toContain('回测任务已完成')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 202')
    expect(wrapper.find('.task-list').text()).not.toContain('Momentum Alpha')
    expect(wrapper.find('.task-list').text()).not.toContain('回测任务已完成')
  })

  it('binds manual failed backtests to the resolved strategy context even when the route query had no strategy id', async () => {
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion Beta',
          strategy_type: 'mean_reversion',
          status: 'paused',
          parameters: [],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: false,
      code: 400,
      message: '风控校验未通过',
      data: null,
      request_id: 'req-backtest-run-error',
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()
    await wrapper.find('.switch-tasks-tab').trigger('click')
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 101')
    expect(wrapper.find('.task-list').text()).toContain('Momentum Alpha')
    expect(wrapper.find('.task-list').text()).toContain('风控校验未通过')
    expect(wrapper.find('.task-list').text()).toContain('FAILED')
  })

  it('keeps the resolved strategy name in reports after a manual successful backtest without a route strategy id', async () => {
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion Beta',
          strategy_type: 'mean_reversion',
          status: 'paused',
          parameters: [],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: {
        task_id: 'bt-unit-006',
        status: 'completed',
        message: '回测任务已完成',
      },
      request_id: 'req-backtest-run-success',
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        total_return: 0.152,
        start_date: '2026-01-01',
        end_date: '2026-03-01',
        completed_at: '2026-03-10T09:30:00Z',
        performance: {
          max_drawdown: 0.045,
        },
      },
      request_id: 'req-backtest-result-success',
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()
    await wrapper.find('.switch-reports-tab').trigger('click')
    await flushPromises()

    expect(wrapper.find('.artdeco-table-row').text()).toContain('Momentum Alpha')
    expect(wrapper.find('.artdeco-table-row').text()).not.toContain('策略 101')
    expect(wrapper.find('.artdeco-table-row').text()).toContain('+15.2%')
  })

  it('does not leak the previous strategy KPI summary into a new route query without its own verified task context', async () => {
    routeMock.query = { strategyId: '101' }
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion',
          strategy_type: 'reversion',
          status: 'draft',
          parameters: [
            { name: 'threshold', value: 3, data_type: 'number' },
          ],
        },
      ],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: {
        task_id: 'bt-unit-005',
        status: 'completed',
        message: '回测任务已完成',
      },
      request_id: 'req-backtest-run-success',
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        total_return: 0.186,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        completed_at: '2026-05-05T09:36:00Z',
        performance: {
          max_drawdown: 0.064,
        },
      },
      request_id: 'req-backtest-result-success',
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.backtest-header-stub button:last-of-type').trigger('click')
    await flushPromises()

    expect(wrapper.find('.backtest-kpi-grid-stub').text()).toContain('总回测次数:3')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 202')
    expect(wrapper.find('.backtest-kpi-grid-stub').text()).not.toContain('总回测次数:3')
    expect(wrapper.find('.backtest-kpi-grid-stub').text()).toContain('总回测次数:2')
  })

  it('does not leak the previous strategy optimization candidates into a new route query without its own verified optimization context', async () => {
    routeMock.query = { strategyId: '101' }
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [
        {
          strategy_id: 101,
          strategy_name: 'Momentum Alpha',
          strategy_type: 'momentum',
          status: 'active',
          parameters: [
            { name: 'lookback', value: 20, data_type: 'number' },
          ],
        },
        {
          strategy_id: 202,
          strategy_name: 'Mean Reversion',
          strategy_type: 'reversion',
          status: 'draft',
          parameters: [
            { name: 'threshold', value: 3, data_type: 'number' },
          ],
        },
      ],
    })
    getSnapshotMock.mockImplementation((strategyId: string) => {
      if (strategyId === '101') {
        return {
          id: '101',
          name: 'Momentum Alpha',
          type: 'momentum',
          status: 'active',
          lastRunTime: '-',
          parameters: {
            lookback: 20,
            position_limit: '32%',
            stop_loss: '2.8%',
            rebalance_frequency: '每 3 天',
          },
          optimization: {
            score: 92,
            recommendedParameters: {
              position_limit: '32%',
              stop_loss: '2.8%',
              rebalance_frequency: '每 3 天',
            },
            writebackTargets: ['backtest'],
            updatedAt: '2026-05-06T10:00:00Z',
          },
        }
      }

      return null
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.switch-optimize-tab').trigger('click')
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 101')
    expect(wrapper.find('.artdeco-table-count').text()).toBe('1')
    expect(wrapper.find('.tab-panel').text()).toContain('Momentum Alpha')
    expect(wrapper.find('.tab-panel').text()).toContain('32%')
    expect(wrapper.find('.tab-panel').text()).toContain('2.8%')

    routeMock.query = { strategyId: '202' }
    await nextTick()
    await flushPromises()

    expect(wrapper.find('.context-strip').text()).toContain('ID 202')
    expect(wrapper.find('.artdeco-table-count').text()).toBe('0')
    expect(wrapper.find('.tab-panel').text()).not.toContain('Momentum Alpha')
    expect(wrapper.find('.tab-panel').text()).not.toContain('32%')
    expect(wrapper.find('.tab-panel').text()).not.toContain('2.8%')
    expect(wrapper.find('.tab-panel').text()).toContain('建议仓位上限')
    expect(wrapper.find('.tab-panel').text()).toContain('建议止损阈值')
    expect(wrapper.find('.tab-panel').text()).toContain('--')
  })
})
